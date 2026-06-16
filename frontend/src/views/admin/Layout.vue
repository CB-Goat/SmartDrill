<template>
  <div class="admin-layout">
    <div class="admin-sidebar">
      <div class="admin-logo">智练通管理后台</div>
      <div class="admin-menu">
        <router-link to="/admin" class="menu-item" exact-active-class="active">仪表盘</router-link>
        <router-link to="/admin/users" class="menu-item" active-class="active">用户管理</router-link>
        <router-link to="/admin/recharges" class="menu-item" active-class="active">充值记录</router-link>
        <router-link to="/admin/orders" class="menu-item" active-class="active">订单管理</router-link>
        <div class="menu-divider"></div>
        <div class="menu-group">教材结构</div>
        <router-link to="/admin/versions" class="menu-item" active-class="active">版本管理</router-link>
        <router-link to="/admin/grades" class="menu-item" active-class="active">年级管理</router-link>
        <router-link to="/admin/subjects" class="menu-item" active-class="active">科目管理</router-link>
        <router-link to="/admin/semesters" class="menu-item" active-class="active">学期管理</router-link>
        <router-link to="/admin/units" class="menu-item" active-class="active">单元管理</router-link>
        <div class="menu-divider"></div>
        <div class="menu-group">内容管理</div>
        <router-link to="/admin/knowledge-exam-points" class="menu-item" active-class="active">知识考点管理</router-link>
        <router-link to="/admin/questions" class="menu-item" active-class="active">题库管理</router-link>
      </div>
      <div class="admin-footer">
        <router-link to="/" class="back-link">返回前台</router-link>
      </div>
    </div>
    <div class="admin-content">
      <router-view />
    </div>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: #f5f5f5;
}

.admin-sidebar {
  width: 240px;
  background: #001529;
  display: flex;
  flex-direction: column;
}

.admin-logo {
  height: 64px;
  line-height: 64px;
  text-align: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  background: #002140;
}

.admin-menu {
  flex: 1;
  padding: 8px 0;
}

.menu-item {
  display: block;
  height: 48px;
  line-height: 48px;
  padding: 0 24px;
  color: rgba(255, 255, 255, 0.65);
  text-decoration: none;
  transition: all 0.3s;
}

.menu-item:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.menu-item.active {
  color: #fff;
  background: #1890ff;
}

.menu-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 8px 24px;
}

.menu-group {
  padding: 8px 24px;
  color: rgba(255, 255, 255, 0.45);
  font-size: 12px;
}

.admin-footer {
  padding: 16px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.back-link {
  color: rgba(255, 255, 255, 0.65);
  text-decoration: none;
}

.back-link:hover {
  color: #fff;
}

.admin-content {
  flex: 1;
  padding: 24px;
  overflow: auto;
}
</style>