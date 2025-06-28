<template>
  <div class="login">
	<p>Login</p>
	<input
		type="text"
		@input="(e) => secret = (e.target.value || '').trim()"
		hidden
	/>
	<input
		type="email"
		placeholder="Email"
		@input="(e) => email = (e.target.value || '').trim()"
	/>
	<input
		type="password"
		placeholder="Password"
		@input="(e) => password = (e.target.value || '').trim()"
	/>
	<button @click="login">Login</button>
	<p v-if="success_message" class="success">{{ success_message }}</p>
	<p v-if="error_message" class="error">{{ error_message }}</p>
  </div>
</template>

<script>
import api from '@/api'

export default {
	name: 'Login',

	components: {
	},

	data() {
		return {
			email: '',
			password: '',
			secret: 'thisissecret',
			success_message: '',
			error_message: '',
		}
	},

	methods: {
		test(a) {
			console.log(a)
		},
		login() {
			if (this.secret != 'thisissecret') {
				// It's a bot
				return
			}
			if (!this.email.includes('@') || !this.email.includes('.')) {
				this.error_message = 'Please enter a valid email address.'
			}

			console.log(this.email)
			console.log(this.password)

			api(`http://127.0.0.1:5000/login/`, 'POST', {
				email: this.email,
				password: this.password
			}).then(response => {
				console.log(response)
				if (response.ok) {
					this.error_message = ''
					this.success_message = response.message
					window.localStorage.setItem('token', response.token)
					window.location.href = '/'
				}
				else {
					this.success_message = ''
					this.error_message = response.message || 'ERROR'
				}
			})
		}
	},
}
</script>

<style>

button {
	margin: 0.25rem;
	padding: 0.5rem 1rem;
	font-family: 'Inter', sans-serif;
	font-size: 0.75rem;
	font-weight: 600;
	color: #ccc;
}

.home {
	position: relative;
	display: flex;
	flex-direction: column;
	align-items: center;
	margin: auto;
	padding: 2rem;
	width: 100%;
}


.document-panel {
	--width: 420px;

	position: fixed;
	top: 0;
	left: calc(var(--width) * -1);
	width: var(--width);
	height: 100%;
	display: flex;
	flex-direction: column;
	padding: 3rem;
	background-color: rgb(21, 22, 24);
	z-index: 99;
	box-shadow: 0px 4px 40px -8px rgba(0,0,0,.5);
	overflow-y: scroll;
	transition: left 0.25s;

	&.open {
		left: 0;
	}

	.documents-title {
		font-size: 1rem;
		font-weight: 600;
		padding-bottom: 2rem;
	}

	.document {
		margin: 0.5rem 0;
		padding: 0.75rem 1rem;
		background-color: rgb(35, 36, 38);
		border-radius: 8px;
		font-size: 0.9rem;
		font-weight: 600;
		cursor: pointer;
		
		&:hover {
			background-color: rgb(42, 43, 45);
		}
	}
}


.toolbar {
	position: fixed;
	top: 0;
	padding: 0.5rem 1rem;
	background-color: rgb(36, 37, 39);
	z-index: 99;
}


.edit-toggle {
	&.on {
		background-color: #197243;
	}
	&.off {
		background-color: #9b2626;
	}
}

.node {
	--color: #f34369;
	--color-faded: #32181d;
	/* --color: #43f3b3;
	--color-faded: #00515a; */
	/* --color: #5d62f9;
	--color-faded: #292a40; */

	position: relative;
	padding: 1rem;
	width: 100%;
	
	&.editing:hover, &.editing:focus {
		background-color: rgba(255,255,255,0.1);
	}

	&.header {
		margin-top: 3rem;
		margin-bottom: 1rem;
		font-weight: 600;
		font-size: 1.25rem;
		color: var(--color);
		border-bottom: 1px solid #333;
	}

	&.highlight {
		width: unset;
		margin-top: 1.5rem;
		margin-bottom: 2rem;
		padding: 0.75rem 1.5rem;
		font-size: 0.9rem;
		text-align: center;
		background-color: var(--color-faded);
		color: var(--color);
		/* border: 1px solid var(--color); */
		box-shadow: 0 4px 16px -8px #000;
		border-radius: 12px;
	}

	&.blockquote {
		margin: 1rem 0;
		padding: 1rem 1.5rem;
		text-align: center;
		color: #777;
	}

	&.line {
		width: 25%;
		height: 1px;
		margin: 3rem 0;
		padding: 0;
		flex-grow: 0;
		flex-shrink: 0;
		border-top: 1px solid #333;
		font-size: 0;
	}
}

#nodes {
	position: relative;
	width: 100%;
	max-width: 780px;
	padding-bottom: 8rem;
}

h1, h2, h3, h4, h5, h6, p {
	padding: 0;
}

h1 {
	margin-top: 3rem;
	margin-bottom: 1rem;
	padding: 1rem 0;
	font-size: 1.25rem;
	font-weight: 600;
	color: #fff;
	/* color: #f34369; */
	border-bottom: 1px solid #333;
}

h2 {
	margin-top: 2rem;
	margin-bottom: 1rem;
	padding: 0.75rem 0;
	font-size: 1.1rem;
	font-weight: 600;
	color: #fff;
	color: #fd597f;
	color: #868cff;
	border-bottom: 1px solid #333;
}

h3 {
	margin-top: 2rem;
	margin-bottom: 1.25rem;
	font-size: 1.25rem;
	font-weight: 400;
	color: #fff;
}

h4 {
	margin-top: 1.5rem;
	margin-bottom: 0.75rem;
	font-size: 1rem;
	font-weight: 600;
	color: #fff;
}

p {
	margin-bottom: 0.75rem;
}

b {
	color: #ff768f;
	color: #989dff;
	color: #72fcbc;
	color: #fff;
	font-weight: 600;
}

ul {
	margin-bottom: 1rem;
}

.node-toolbar {
	position: fixed;
	top: 0;
	left: 50%;
	transform: translate(-50%, -100%);

	button {
		--button-size: 32px;
		width: var(--button-size);
		height: var(--button-size);
	}
}

.save-indicator {
	position: fixed;
	top: 1rem;
	right: 2rem;
}

.saving {
	--pending-color: rgb(213, 172, 117);
	--success-color: rgb(108, 225, 149);
	--error-color: rgb(244, 96, 114);

	display: flex;
	justify-content: center;
	align-items: center;

	span {
		margin-left: 0.75rem;
		font-size: 0.75rem;
		font-weight: 500;
		color: #aaa;
	}

	&.pending {
		span { color: var(--pending-color); }
		.saving-loader { border-color: var(--pending-color); }
	}

	&.success {
		span { color: var(--success-color); }
		.saving-loader { border-color: var(--success-color); }
	}

	&.error {
		span { color: var(--error-color); }
		.saving-loader { border-color: var(--error-color); }
	}
}

@keyframes rotate {
	0% { transform: rotate(0deg); }
	100% { transform: rotate(360deg); }
}

.saving-loader {
	--size: 1.25rem;

	position: relative;
	width: var(--size);
	height: var(--size);
	border-radius: 100%;
	border: 2px solid #aaa;
	border-bottom: 2px solid transparent !important;
	border-right: 2px solid transparent !important;
	animation-name: rotate;
	animation-timing-function: linear;
	animation-iteration-count: infinite;
	animation-duration: 0.75s;
}

</style>
