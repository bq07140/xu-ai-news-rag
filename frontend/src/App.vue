<template>
  <router-view />
</template>

<script setup>
// App根组件
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
  font-size: 15px; /* Increased from default 16px for better readability with English text */
}

/* Optimize Element Plus components font size */
.el-button {
  font-size: 14px;
}

.el-table {
  font-size: 14px;
}

.el-input__inner {
  font-size: 14px;
}

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>


