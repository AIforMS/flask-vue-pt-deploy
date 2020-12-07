<template>
  <div class="alert" role="alert" v-bind:class="'alert-' + variant">
    {{ message }}
  </div>
</template>

<script>
export default {
  props: ['variant', 'message']
}
</script>

<style scoped>
  /* Import Bootstrap css files */
  @import 'bootstrap/dist/css/bootstrap.css';
</style>
