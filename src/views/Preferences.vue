<template>
  <div class="preferences-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div>
            <h2>口味偏好管理</h2>
            <p>
              当前用户可以添加多条口味偏好记录，并设置其中一条为默认偏好。
              AI 分析、AI 对话和饮食计划默认使用“默认偏好”。
            </p>
          </div>

          <div>
            <el-button @click="loadPreferences">刷新</el-button>
            <el-button type="primary" @click="openCreateDialog">
              新增口味偏好
            </el-button>
          </div>
        </div>
      </template>

      <el-alert
        :title="`当前用户：${userStore.currentUser?.username || 'demo_user'}（ID：${currentUserId}）`"
        type="info"
        show-icon
        :closable="false"
        class="mb-16"
      />

      <el-table
        v-loading="loading"
        :data="preferences"
        border
        empty-text="暂无口味偏好，请先新增"
      >
        <el-table-column type="index" label="序号" width="70" />

        <el-table-column prop="id" label="偏好ID" width="90" />

        <el-table-column prop="preference_name" label="偏好名称" min-width="150" />

        <el-table-column label="默认" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.is_default === 1" type="success">
              默认
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column label="喜欢口味" min-width="180">
          <template #default="{ row }">
            {{ joinList(row.preferred_flavors) }}
          </template>
        </el-table-column>

        <el-table-column label="不喜欢食物" min-width="180">
          <template #default="{ row }">
            {{ joinList(row.disliked_foods) }}
          </template>
        </el-table-column>

        <el-table-column label="偏好菜系" min-width="180">
          <template #default="{ row }">
            {{ joinList(row.preferred_cuisines) }}
          </template>
        </el-table-column>

        <el-table-column label="过敏食物" min-width="160">
          <template #default="{ row }">
            {{ joinList(row.allergies) }}
          </template>
        </el-table-column>

        <el-table-column label="餐次" width="90">
          <template #default="{ row }">
            {{ row.meal_count || '-' }} 餐
          </template>
        </el-table-column>

        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">
              编辑
            </el-button>

            <el-button
              size="small"
              type="success"
              :disabled="row.is_default === 1"
              @click="handleSetDefault(row)"
            >
              设为默认
            </el-button>

            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑口味偏好' : '新增口味偏好'"
      width="900px"
    >
      <el-form :model="form" label-width="120px">
        <el-form-item label="偏好名称">
          <el-input
            v-model="form.preference_name"
            placeholder="例如：默认偏好、减脂期偏好、高尿酸饮食偏好"
          />
        </el-form-item>

        <el-form-item label="喜欢的口味">
          <el-select
            v-model="form.preferred_flavors"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="例如：清淡、少油、鲜香"
            style="width: 100%"
          >
            <el-option label="清淡" value="清淡" />
            <el-option label="少油" value="少油" />
            <el-option label="少盐" value="少盐" />
            <el-option label="鲜香" value="鲜香" />
            <el-option label="微辣" value="微辣" />
            <el-option label="酸甜" value="酸甜" />
          </el-select>
        </el-form-item>

        <el-form-item label="不喜欢的食物">
          <el-select
            v-model="form.disliked_foods"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="例如：香菜、苦瓜、肥肉"
            style="width: 100%"
          >
            <el-option label="香菜" value="香菜" />
            <el-option label="苦瓜" value="苦瓜" />
            <el-option label="肥肉" value="肥肉" />
            <el-option label="动物内脏" value="动物内脏" />
            <el-option label="辣椒" value="辣椒" />
          </el-select>
        </el-form-item>

        <el-form-item label="偏好菜系">
          <el-select
            v-model="form.preferred_cuisines"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="例如：粤菜、江浙菜、家常菜"
            style="width: 100%"
          >
            <el-option label="粤菜" value="粤菜" />
            <el-option label="川菜" value="川菜" />
            <el-option label="湘菜" value="湘菜" />
            <el-option label="江浙菜" value="江浙菜" />
            <el-option label="家常菜" value="家常菜" />
            <el-option label="素食" value="素食" />
          </el-select>
        </el-form-item>

        <el-form-item label="过敏食物">
          <el-select
            v-model="form.allergies"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="例如：花生、牛奶、鸡蛋、海鲜"
            style="width: 100%"
          >
            <el-option label="花生" value="花生" />
            <el-option label="牛奶" value="牛奶" />
            <el-option label="鸡蛋" value="鸡蛋" />
            <el-option label="海鲜" value="海鲜" />
            <el-option label="坚果" value="坚果" />
          </el-select>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="烹饪时间">
              <el-input-number
                v-model="form.cooking_time_limit"
                :min="10"
                :max="180"
                :step="5"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>

          <el-col :span="6">
            <el-form-item label="难度偏好">
              <el-select v-model="form.difficulty_preference" style="width: 100%">
                <el-option label="简单" value="easy" />
                <el-option label="中等" value="medium" />
                <el-option label="复杂" value="hard" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="6">
            <el-form-item label="预算水平">
              <el-select v-model="form.budget_level" style="width: 100%">
                <el-option label="低预算" value="low" />
                <el-option label="中等预算" value="medium" />
                <el-option label="高预算" value="high" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="6">
            <el-form-item label="每日餐次">
              <el-input-number
                v-model="form.meal_count"
                :min="2"
                :max="6"
                :step="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="设为默认">
          <el-switch
            v-model="form.is_default"
            :active-value="1"
            :inactive-value="0"
            active-text="是"
            inactive-text="否"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitPreference">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createPreferences,
  deletePreference,
  listPreferencesByUser,
  setDefaultPreference,
  updatePreferenceById
} from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const currentUserId = computed(() => userStore.userId || 1)

const preferences = ref<any[]>([])
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const createEmptyForm = () => ({
  preference_name: '',
  is_default: 0,
  preferred_flavors: [] as string[],
  disliked_foods: [] as string[],
  preferred_cuisines: [] as string[],
  allergies: [] as string[],
  cooking_time_limit: 45,
  difficulty_preference: 'medium',
  budget_level: 'medium',
  meal_count: 3
})

const form = reactive(createEmptyForm())

function resetForm() {
  Object.assign(form, createEmptyForm())
  editingId.value = null
}

async function loadPreferences() {
  loading.value = true

  try {
    const res = await listPreferencesByUser(currentUserId.value)

    if (res.success) {
      preferences.value = res.data || []
    } else {
      ElMessage.error(res.message || '获取口味偏好失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取口味偏好失败，请检查后端服务')
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  resetForm()
  form.preference_name = `偏好${preferences.value.length + 1}`

  if (preferences.value.length === 0) {
    form.is_default = 1
  }

  dialogVisible.value = true
}

function openEditDialog(row: any) {
  resetForm()

  editingId.value = row.id
  form.preference_name = row.preference_name || ''
  form.is_default = row.is_default || 0
  form.preferred_flavors = row.preferred_flavors || []
  form.disliked_foods = row.disliked_foods || []
  form.preferred_cuisines = row.preferred_cuisines || []
  form.allergies = row.allergies || []
  form.cooking_time_limit = row.cooking_time_limit || 45
  form.difficulty_preference = row.difficulty_preference || 'medium'
  form.budget_level = row.budget_level || 'medium'
  form.meal_count = row.meal_count || 3

  dialogVisible.value = true
}

async function submitPreference() {
  if (!form.preference_name) {
    ElMessage.warning('请输入偏好名称')
    return
  }

  submitting.value = true

  const payload = {
    preference_name: form.preference_name,
    is_default: form.is_default,
    preferred_flavors: form.preferred_flavors,
    disliked_foods: form.disliked_foods,
    preferred_cuisines: form.preferred_cuisines,
    allergies: form.allergies,
    cooking_time_limit: form.cooking_time_limit,
    difficulty_preference: form.difficulty_preference,
    budget_level: form.budget_level,
    meal_count: form.meal_count
  }

  try {
    let res

    if (editingId.value) {
      res = await updatePreferenceById(editingId.value, payload)
    } else {
      res = await createPreferences(currentUserId.value, payload)
    }

    if (res.success) {
      ElMessage.success(res.message || '保存成功')
      dialogVisible.value = false
      await loadPreferences()
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (error: any) {
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '保存失败')
  } finally {
    submitting.value = false
  }
}

async function handleSetDefault(row: any) {
  try {
    const res = await setDefaultPreference(row.id)

    if (res.success) {
      ElMessage.success('已设置为默认偏好')
      await loadPreferences()
    } else {
      ElMessage.error(res.message || '设置默认失败')
    }
  } catch (error: any) {
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '设置默认失败')
  }
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm(
      `确定删除口味偏好「${row.preference_name || row.id}」吗？`,
      '删除确认',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      }
    )

    const res = await deletePreference(row.id)

    if (res.success) {
      ElMessage.success('删除成功')
      await loadPreferences()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error(error?.response?.data?.detail || '删除失败')
    }
  }
}

function joinList(list: string[]) {
  return list && list.length > 0 ? list.join('、') : '-'
}

onMounted(() => {
  loadPreferences()
})

watch(
  () => currentUserId.value,
  () => {
    preferences.value = []
    resetForm()
    dialogVisible.value = false
    loadPreferences()
  }
)
</script>

<style scoped>
.preferences-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
}

.card-header p {
  margin: 6px 0 0;
  color: #666;
  font-size: 14px;
}

.mb-16 {
  margin-bottom: 16px;
}
</style>