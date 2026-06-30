<!-- <template>
  <div id="app-root">
    <el-header class="app-header" v-if="userStore.isLoggedIn">
      <div class="header-content">
        <div class="logo" @click="router.push('/')">
          <el-icon :size="28"><Food /></el-icon>
          <span class="logo-text">AI营养师</span>
        </div>
        <div class="nav-menu">
          <el-menu :default-active="route.path" mode="horizontal" router>
            <el-menu-item index="/dashboard"><el-icon><DataAnalysis /></el-icon><span>控制台</span></el-menu-item>
            <el-menu-item index="/health"><el-icon><FirstAidKit /></el-icon><span>体检报告</span></el-menu-item>
            <el-menu-item index="/preferences"><el-icon><Setting /></el-icon><span>口味偏好</span></el-menu-item>
            <el-menu-item index="/meal-plan"><el-icon><Bowl /></el-icon><span>智能食谱</span></el-menu-item>
            <el-menu-item index="/chat"><el-icon><ChatDotRound /></el-icon><span>AI咨询</span></el-menu-item>
          </el-menu>
        </div>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Food, DataAnalysis, FirstAidKit, Setting, Bowl, ChatDotRound } from '@element-plus/icons-vue'
import { User, Menu, HomeFilled } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

onMounted(() => {
  userStore.init()
})
</script>
 -->

 <template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">AI营养师系统</div>

      <el-menu
        router
        :default-active="route.path"
        class="menu"
      >
        <el-menu-item index="/dashboard">
          数据看板
        </el-menu-item>

        <el-menu-item index="/users">
          用户管理
        </el-menu-item>

        <el-menu-item index="/health">
          体检报告
        </el-menu-item>

        <el-menu-item index="/preferences">
          口味偏好
        </el-menu-item>

        <el-menu-item index="/meal-plan">
          饮食计划
        </el-menu-item>

        <el-menu-item index="/chat">
          AI营养师对话
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
            AI营养师后台管理系统
        </div>

        <div class="header-right">
           <el-tag type="success" effect="plain">
               当前用户：{{ currentUsername }}(ID:{{ currentUserId }})
           </el-tag>

           <el-button size="small" type="primary" @click="goUsers">
               切换用户
           </el-button>
        </div>
      </el-header>

      <el-main class="main">
        <router-view :key="$route.fullPath" />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const currentUserId = computed(() => userStore.userId || 1)
const currentUsername = computed(() => userStore.currentUser?.username || 'demo_user')

function goUsers() {
  router.push('/users')
}

onMounted(() => {
  userStore.init()
})
</script>

<style scoped>
.layout {
  height: 100vh;
  width: 100vw;
}

.aside {
  background-color: #ffffff;
  border-right: 1px solid #e5e7eb;
}

.logo {
  height: 60px;
  line-height: 60px;
  padding-left: 20px;
  font-size: 20px;
  font-weight: bold;
  border-bottom: 1px solid #e5e7eb;
}

.menu {
  height: calc(100vh - 60px);
  border-right: none;
}

.header {
  height: 60px;
  line-height: 60px;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  font-size: 20px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  font-size: 20px;
  font-weight: bold;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: normal;
}

.main {
  background-color: #f5f7fa;
  padding: 24px;
}
</style>