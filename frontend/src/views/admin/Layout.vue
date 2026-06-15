<template>
  <div class="page">
    <van-nav-bar title="管理后台" left-arrow @click-left="$router.push('/')" />
    <van-cell-group inset style="margin: 16px">
      <van-cell title="用户管理" is-link to="/admin/users" />
      <van-cell title="充值记录" is-link to="/admin/recharges" />
      <van-cell title="订单管理" is-link to="/admin/orders" />
      <van-cell title="知识点管理" is-link to="/admin/knowledge" />
      <van-cell title="题库管理" is-link to="/admin/questions" />
    </van-cell-group>
    <router-view />
  </div>
</template>