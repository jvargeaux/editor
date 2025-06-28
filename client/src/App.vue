<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>

export default {
	name: 'App',
	components: {

	}
}

</script>

<style lang="scss">

* {
	margin: 0;
	outline: none;
	box-sizing: border-box;
}

html {
	font-family: Avenir, Helvetica, Arial, sans-serif;
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
	color: #d9d9d9;
	background-color: rgb(29, 30, 32);
}

body {
	display: flex;
	justify-content: center;
	// font-family: "Open Sans", sans-serif;
	// font-family: "Noto Sans", sans-serif;
	font-family: "Inter", sans-serif;
	font-optical-sizing: auto;
	font-weight: 400;
	line-height: 1.75em;
	letter-spacing: -0.1px;
	font-style: normal;
}

#app {
	position: relative;
	width: 100%;
}

button {
	border: 0;
	border-radius: 4px;
	background-color: #333;
	padding: 0.25rem 0.75rem;
	cursor: pointer;
	
	&:hover {
		background-color: #444;
	}
}

</style>
