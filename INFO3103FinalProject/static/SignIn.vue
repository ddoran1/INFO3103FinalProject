<template>
`
<div id="signin">
<form>
  Username:<br>
  <input type="text" name="Username"><br>
  Password:<br>
  <input type="text" name="Password"><br>
</form>
  <p>{{ message }}</p>
  <button v-on:click="submit">Submit</button>
  <button v-on:click="submit">Submit</button>
</div>
`
</template>

<script>

	var signIn = new Vue ({
		el: '#signin',
		data: {
			message: 'Sign in or click here to sign up'
		},

		methods: {
			submit: function () {
				let userName = document.getElementById("Username").value
				let password = document.getElementById("Password").value
				this.message = SignUpPost(userName, password)
			}
		}
	})

</script>

<style>

</style>
