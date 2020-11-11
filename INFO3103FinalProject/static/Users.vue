<template>
`
	<div class="container">
		<div class="container">
			<p>Users:<br></p>
			<ul id = "usersLists">
				<li v-for="u in Users">
					{{ u.UserName }}
				</li>
			</ul>
		</div>
	</div>
`
</template>

<script>

	var usersLists = new Vue ({
		el: '#usersLists',
		data: {
			Users: [
				{UserName: usersGet()}
			]
		}
   usersGet : function (){
      let axiosConfig = {
          headers: {
              'Content-Type': 'application/json;charset=UTF-8',
              "Access-Control-Allow-Origin": "*",
          }
      };

      axios.get('https://info3103.cs.unb.ca:' + location.port + '/users', axiosConfig)
        .then((res) => {
          app.addedSch=res.data;
        })
        .catch((err) => {
          app.addedSch= err;
      });
    },//usersGet

</script>

<style>

</style>
