<template>
`
<div id="signup">
<form>
  Username:<br>
  <input type="text" name="Username"><br>
  Password:<br>
  <input type="text" name="Password"><br>
  Email:<br>
  <input type="text" name="Email"><br>
</form>
  <p>{{ message }}</p>
  <button v-on:click="submit">Submit</button>
</div>
`
</template>

<script>

	var signUp = new Vue ({
		el: '#signup',
		data: {
			message: 'Fill in fields and click Submit to sign up'
		},

		methods: {
			submit: function () {
				let userName = document.getElementById("Username").value
				let password = document.getElementById("Password").value
				let email = document.getElementById("Email").value
				this.message = SignUpPost(userName, password, email)
			}
		}
	})

</script>

<style>

</style>
