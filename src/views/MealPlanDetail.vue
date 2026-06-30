<template>
  <div style="padding: 24px;">
    <h2>饮食计划详情</h2>
    <p>当前计划 ID：{{ planId }}</p>

    <el-card>
      <p>这里用于展示某个饮食计划的详细内容。</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const planId = computed(() => route.params.planId)
</script>