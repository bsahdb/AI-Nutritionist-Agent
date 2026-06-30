<template>
  <div class="user-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div>
            <h2>用户管理</h2>
            <p>新增用户并切换当前用户。当前用户会影响体检报告、口味偏好、AI分析和饮食计划。</p>
          </div>

          <div>
            <el-button @click="loadUsers">刷新</el-button>
            <el-button type="primary" @click="openCreateDialog">
              新增用户
            </el-button>
          </div>
        </div>
      </template>

      <el-alert
        :title="`当前用户：${userStore.currentUser?.username || '未加载'}（ID：${userStore.userId}）`"
        type="success"
        show-icon
        :closable="false"
        class="mb-16"
      />

      <el-table
        v-loading="loading"
        :data="users"
        border
        empty-text="暂无用户"
      >
        <el-table-column type="index" label="序号" width="70" />
        <el-table-column prop="id" label="用户ID" width="90" />
        <el-table-column prop="username" label="用户名" min-width="160" />
        <el-table-column prop="gender" label="性别" width="100" />
        <el-table-column prop="age" label="年龄" width="100" />
        <el-table-column prop="height_cm" label="身高(cm)" width="120" />
        <el-table-column prop="weight_kg" label="体重(kg)" width="120" />
        <el-table-column prop="bmi" label="BMI" width="100" />

        <el-table-column label="健康目标" min-width="180">
          <template #default="{ row }">
            {{ joinList(row.health_goals) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="success"
              :disabled="row.id === userStore.userId"
              @click="handleSetCurrentUser(row)"
            >
              {{ Number(row.id) === Number(userStore.userId) ? '当前用户' : '设为当前用户' }}
            </el-button>

            <el-button size="small" @click="openEditDialog(row)">
              编辑
            </el-button>

            <el-button
              size="small"
              type="danger"
              :disabled="row.id === 1"
              @click="removeUser(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑用户' : '新增用户'"
      width="650px"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" :disabled="!!editingId" placeholder="例如：user_zhangsan" />
        </el-form-item>

        <el-form-item v-if="!editingId" label="密码">
          <el-input v-model="form.password" type="password" placeholder="默认 123456" show-password />
        </el-form-item>

        <el-form-item label="性别">
          <el-select v-model="form.gender" style="width: 100%">
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="年龄">
          <el-input-number v-model="form.age" :min="1" :max="120" style="width: 100%" />
        </el-form-item>

        <el-form-item label="身高(cm)">
          <el-input-number v-model="form.height_cm" :min="50" :max="250" :step="1" style="width: 100%" />
        </el-form-item>

        <el-form-item label="体重(kg)">
          <el-input-number v-model="form.weight_kg" :min="20" :max="300" :step="1" style="width: 100%" />
        </el-form-item>

        <el-form-item label="健康目标">
          <el-select
            v-model="form.health_goals"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="例如：减脂、控糖、低嘌呤"
            style="width: 100%"
          >
            <el-option label="健康管理" value="general_health" />
            <el-option label="减脂" value="weight_loss" />
            <el-option label="控糖" value="blood_sugar_control" />
            <el-option label="控压" value="blood_pressure_control" />
            <el-option label="低嘌呤" value="low_purine" />
            <el-option label="降血脂" value="lipid_control" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitUser">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createUser, deleteUser, listUsers, updateUser } from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const users = ref<any[]>([])
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const form = reactive({
  username: '',
  password: '',
  gender: 'male',
  age: 30,
  height_cm: 170,
  weight_kg: 65,
  health_goals: [] as string[]
})

function handleSetCurrentUser(row: any) {
  userStore.setCurrentUser({
    id: row.id,
    username: row.username
  })

  ElMessage.success(`已切换当前用户：${row.username}`)
}

function resetForm() {
  form.username = ''
  form.password = ''
  form.gender = 'male'
  form.age = 30
  form.height_cm = 170
  form.weight_kg = 65
  form.health_goals = []
  editingId.value = null
}

async function loadUsers() {
  loading.value = true

  try {
    const res = await listUsers()

    if (res.success) {
      users.value = res.data || []
    } else {
      ElMessage.error(res.message || '获取用户列表失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(row: any) {
  resetForm()

  editingId.value = row.id
  form.username = row.username
  form.gender = row.gender || 'male'
  form.age = row.age || 30
  form.height_cm = row.height_cm || 170
  form.weight_kg = row.weight_kg || 65
  form.health_goals = row.health_goals || []

  dialogVisible.value = true
}

async function submitUser() {
  if (!form.username) {
    ElMessage.warning('请输入用户名')
    return
  }

  submitting.value = true

  try {
    let res

    if (editingId.value) {
      res = await updateUser(editingId.value, {
        gender: form.gender,
        age: form.age,
        height_cm: form.height_cm,
        weight_kg: form.weight_kg,
        health_goals: form.health_goals
      })
    } else {
      res = await createUser({
        username: form.username,
        password: form.password || '123456',
        gender: form.gender,
        age: form.age,
        height_cm: form.height_cm,
        weight_kg: form.weight_kg,
        health_goals: form.health_goals
      })
    }

    if (res.success) {
      ElMessage.success(res.message || '保存成功')
      dialogVisible.value = false

      if (!editingId.value) {
        await userStore.setCurrentUser(res.data)
      }

      await loadUsers()
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

async function removeUser(row: any) {
  try {
    await ElMessageBox.confirm(
      `确定删除用户「${row.username}」吗？该用户关联的体检报告、口味偏好和饮食计划也会删除。`,
      '删除确认',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      }
    )

    const res = await deleteUser(row.id)

    if (res.success) {
      ElMessage.success('删除成功')

      if (row.id === userStore.userId) {
        await userStore.fetchUser(1)
      }

      await loadUsers()
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

onMounted(async () => {
  await userStore.init()
  await loadUsers()
})
</script>

<style scoped>
.user-page {
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