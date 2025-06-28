export default function(endpoint, method, body) {
	return fetch(endpoint, {
		method,
		headers: {
			'Content-Type': 'application/json',
			'Authorization': window.localStorage.getItem('token') || ''
		},
		body: JSON.stringify(body),
	})
		.then(r => {
			if (r.status == 404) return r
			return r.json().then(json => {
				return {
					...json,
					ok: r.ok,
					status: r.status
				}
			})
		})
}