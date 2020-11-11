<template>
`
<div id="user">
  <p>{{ message }}</p>
  <button v-on:click="delete">Delete</button>
</div>
`
</template>

<script>

var user = new Vue ({
		let ref = window.location.href
		let id = ref.split("/")
		el: '#user',
		data: {
			Users: [
				message: userGet(id[1])
			]
		},

		methods: {
			delete: function () {
				this.message = userDelete(id[1])
			}
		}
})

</script>

<style>

</style>
