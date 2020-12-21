<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light" style="margin-bottom: 20px;">
    <div class="container">
      <router-link to="/" class="navbar-brand">
        <!-- <img src="../assets/icons/palette.svg" width="30" height="30" class="d-inline-block align-top" alt=""> -->
          MICCAI
      </router-link>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav mr-auto mt-2 mt-lg-0">
          <li class="nav-item active">
            <router-link to="/" class="nav-link">首页<span class="sr-only">(current)</span></router-link>
          </li>
          <li class="nav-item">
            <label for="select" class="control-label nav-link disabled"></label>
          </li>
          <li class="nav-item">
            <!-- <a class="nav-link disabled" href="#">工具箱</a> -->
            <select class="selectpicker form-control" id="select">
                <option disabled selected hidden>工具箱</option>
                <option value="seg">
                  <router-link to="/" class="nav-link">分割</router-link>
                </option>
                <!-- <option value="reg">配准</option>
                <option value="fus">融合</option>
                <option value="cla">分类</option> -->
            </select>
            <!-- 把分割、配准、融合、分类都放在这里，作为选项 -->
          </li>
        </ul>

        <!-- <form class="form-inline navbar-left mr-auto">
          <input class="form-control mr-sm-2" type="search" placeholder="Search"> -->
          <!-- 暂时先禁止提交，后续实现搜索再改回 type="submit" -->
          <!-- <button class="btn btn-outline-success my-2 my-sm-0" type="button">Search</button>
        </form> -->

        <ul v-if="sharedState.is_authenticated" class="nav navbar-nav navbar-right">          
          <!-- <li class="nav-item">
            <a class="nav-link disabled" href="#">Messages</a>
          </li>
          <li class="nav-item">
            <router-link to="/profile" class="nav-link">Profile</router-link>
          </li> -->
          <li class="nav-item">
            <a v-on:click="handlerLogout" class="nav-link" href="#">退出</a>
          </li>
        </ul>
        <ul v-else class="nav navbar-nav navbar-right">          
          <li class="nav-item">
            <router-link to="/login" class="nav-link">登录</router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import store from '../store.js'

export default {
  name: 'Navbar',  //this is the name of the component
  data () {
      return {
          sharedState: store.state
      }
  },
  methods: {
      handlerLogout (e) {
          console.log('before logout: ' + this.sharedState.is_authenticated)
          store.logoutAction()
          console.log('after logout: ' + this.sharedState.is_authenticated)
          this.$router.push('/login')
      }
  }
}
</script>

<style scoped>
  /* Import Bootstrap css files */
  @import 'bootstrap/dist/css/bootstrap.css';
</style>
