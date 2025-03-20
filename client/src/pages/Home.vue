<template>
  <div class="home">
	<h3>Editor</h3>
	
	<br>
	<button
		@click="editing = !editing"
		:class="`edit-toggle ${editing ? 'on' : 'off'}`"
	>{{ editing ? 'Editing On' : 'Editing Off' }}</button>
	<button
		@click="saveDocument"
		class="edit-toggle"
	>Save</button>
	<br>
	<br>
	<br>

	<div id="nodes" :contenteditable="editing">
		<p class="node header">This is a header</p>
		<p>This is <span class="bold">highlighted</span> text.</p>
		<p class="node blockquote">This is a blockquote</p>
		<p>Suscipit aliquam integer auctor mi nibh pretium ultrices ut, faucibus himenaeos nulla volutpat luctus nisi nullam consequat, rhoncus dui turpis dapibus litora tortor egestas. Duis magnis commodo conubia rutrum venenatis consequat leo cursus urna, massa aliquam donec sapien sociis maecenas pulvinar in nostra nisl, egestas libero phasellus sociosqu mattis neque vulputate a. Suspendisse nulla blandit vitae libero interdum ornare, fringilla varius tempor curabitur eu, praesent volutpat convallis dapibus tellus.</p>

		<!-- <p
			v-for="(node, index) in nodes"
			:id="node.id"
			:class="`node ${editing ? 'editing' : ''} ${node.type || ''}`"
			@focus="selectedNode = { index: index, id: node.id }"
			@blur="selectedNode = { index: null, id: null }"
		>
			<span v-for="(subnode, subnode_index) in node.content"
				:class="subnode.class"
				@keydown="onNodeInput"
			>{{ subnode.text }}</span>
			<div
				v-if="selectedNode.id == node.id"
				class="node-toolbar"
			>
				<button
					@mousedown="deleteNode(index)"
				>x</button>
				<button
					@mousedown="nodes[index].type = 'header'"
				>H1</button>
				<button
					@mousedown="nodes[index].type = 'paragraph'"
				>P</button>
				<button
					@mousedown="nodes[index].type = 'highlight'"
				>B</button>
				<button
					@mousedown="nodes[index].type = 'blockquote'"
				>Q</button>
			</div>
		</p> -->
	</div>

  </div>
</template>

<script>

export default {
  name: 'Home',

  components: {
  },

	data() {
		return {
			editing: true,
			selectedNode: {
				index: null,
				id: null
			},
			lastID: 99,
			nodes: [
				{
					id: 0,
					type: 'header',
					content: [
						{
							text: 'Introduction'
						}
					]
				},
				{
					id: 1,
					type: 'paragraph',
					content: [
						{
							text: 'This is the '
						},
						{
							class: 'bold',
							text: 'first'
						},
						{
							text: ' line.'
						}
					]
				},
				{
					id: 2,
					type: 'blockquote',
					content: [
						{
							text: 'This is a blockquote.'
						}
					]
				},
				{
					id: 3,
					type: 'line',
				},
				{
					id: 4,
					type: 'paragraph',
					content: [
						{
							text: 'Suscipit aliquam integer auctor mi nibh pretium ultrices ut, faucibus himenaeos nulla volutpat luctus nisi nullam consequat, rhoncus dui turpis dapibus litora tortor egestas. Duis magnis commodo conubia rutrum venenatis consequat leo cursus urna, massa aliquam donec sapien sociis maecenas pulvinar in nostra nisl, egestas libero phasellus sociosqu mattis neque vulputate a. Suspendisse nulla blandit vitae libero interdum ornare, fringilla varius tempor curabitur eu, praesent volutpat convallis dapibus tellus.'
						}
					]
				}
			],
			undo_history: [],
			undo_step: 1,
			max_undo_history: 10
		}
	},

	methods: {
		api(endpoint, method, body) {
			fetch(`/${endpoint}`, {
				method,
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(body),
			})
				.then(r => {
					return {
						request: r,
						json: r.json()
					}
				})
				.then(( request, json ) => {
					console.log(request)
					if (request?.ok) console.log(json)
				})
		},

		saveDocument() {
			this.api('save/asdfasdfas', 'POST', {
				document: document.getElementById('nodes').innerHTML
			})
		},

		updateUndoHistory() {
			this.undo_history.push(JSON.stringify(this.nodes))
			this.undo_history = this.undo_history.slice(-this.max_undo_history)
			window.localStorage.setItem('undo_history', this.undo_history)
			console.log(this.undo_history)
		},

		undo() {
			if (this.undo_step < this.undo_history.length) {
				this.undo_step++
			}
			const step = -this.undo_step
			this.nodes = JSON.parse(this.undo_history.slice(step).shift())
		},

		redo() {
			if (this.undo_step > 1) {
				this.undo_step--
			}
			const step = -this.undo_step
			this.nodes = JSON.parse(this.undo_history.slice(step).shift())
		},

		getSelectionInfo() {
			const selection = window.getSelection()

			// Return empty if nodes are empty
			if (!selection.baseNode || !selection.extentNode) {
				return {
					"start_node_index": -1,
					"start_offset": -1,
					"start_node_content": '',
					"end_node_index": -1,
					"end_offset": -1,
					"end_node_content": '',
					"has_selection": false
				}
			}

			// parent -> node -> text (baseNode / extentNode)
			const base = {
				node: selection.baseNode,
				node_index: Array.prototype.indexOf.call(selection.baseNode.parentElement.parentElement.children, selection.baseNode.parentElement),
				subnode_index: Array.prototype.indexOf.call(selection.baseNode.parentElement.children, selection.baseNode),
				offset: selection.baseOffset
			}
			const extent = {
				node: selection.extentNode,
				node_index: Array.prototype.indexOf.call(selection.extentNode.parentElement.parentElement.children, selection.extentNode.parentElement),
				subnode_index: Array.prototype.indexOf.call(selection.extentNode.parentElement.children, selection.extentNode),
				offset: selection.extentOffset
			}
			
			// If nodes are reversed, flip base and extent
			let start = base.node_index <= extent.node_index ? { ...base } : { ...extent }
			let end = base.node_index <= extent.node_index ? { ...extent } : { ...base }

			if (base.node_index == extent.node_index) {
				// If nodes are the same but subnodes are reversed, flip base and extent 
				if (base.subnode_index > extent.subnode_index) {
					start = extent
					end = base
				}
				// If nodes and subnodes are the same but offsets are reversed, flip offsets
				if (base.subnode_index == extent.subnode_index && base.offset > extent.offset) {
					start.offset = extent.offset
					end.offset = base.offset
				}
			}

			// return {
			// 	"start_node_index": start.node_index,
			// 	"start_subnode_index": start.subnode_index,
			// 	"start_offset": start.offset,
			// 	"start_text": start.node.textContent,
			// 	"end_node_index": end.node_index,
			// 	"end_subnode_index": end.subnode_index,
			// 	"end_offset": end.offset,
			// 	"end_text": end.node.textContent,
			// 	"has_selection": selection.baseNode != selection.extentNode || selection.baseOffset != selection.extentOffset
			// }
			return {
				"start_node": start.node,
				"start_offset": start.offset,
				"end_node": end.node,
				"end_offset": end.offset,
				"has_selection": selection.baseNode != selection.extentNode || selection.baseOffset != selection.extentOffset
			}
		},

		deleteSelection(selection_info) {
			const {
				start_node_index,
				start_subnode_index,
				start_offset,
				start_text,
				end_node_index,
				end_subnode_index,
				end_offset,
				end_text
			} = selection_info
			
			const text_before = start_text.slice(0, start_offset)
			const text_after = end_text.slice(end_offset)

			// Combine before and after text into start node and subnode
			this.$set(this.nodes[start_node_index].content, start_subnode_index, {
				...this.nodes[start_node_index].content[start_subnode_index],
				text: text_before + text_after
			})

			if (start_node_index == end_node_index) {
				// If nodes and subnodes are the same, we're done
				if (start_subnode_index == end_subnode_index) {
					return
				}

				// If nodes are the same, remove all subnodes between start and end, and we're done
				this.nodes[start_node_index].content.splice(start_subnode_index + 1, end_subnode_index)
				return
			}

			// At start node, remove all subnodes after
			this.nodes[start_node_index].content.splice(start_subnode_index + 1, Infinity)
			// At end node, remove all subnodes before
			this.nodes[end_node_index].content.splice(0, end_subnode_index + 1)
			// Merge remaining subnodes from end onto start node
			this.nodes[start_node_index].content = [
				...this.nodes[start_node_index].content,
				...this.nodes[end_node_index].content
			]

			// Remove end node and any other nodes in between
			this.nodes.splice(start_node_index + 1, end_node_index - start_node_index)
		},

		boldSelection(selection_info) {
			const {
				start_node_index,
				start_subnode_index,
				start_offset,
				start_text,
				end_node_index,
				end_subnode_index,
				end_offset,
				end_text
			} = selection_info

			if (start_node_index == end_node_index) {

				const subnode_before = {
					...this.nodes[start_node_index].content[start_subnode_index],
					text: start_text.slice(0, start_offset)
				}
				const subnode_after = {
					...this.nodes[start_node_index].content[end_subnode_index],
					text: end_text.slice(end_offset)
				}

				let new_text = start_text.slice(start_offset, end_offset)

				// Combine text from all subnodes falling within selection
				if (start_subnode_index != end_subnode_index) {
					const end_of_before_text = start_text.slice(start_offset)
					const start_of_after_text = end_text.slice(0, end_offset)
					
					new_text = end_of_before_text
					for (let i = start_subnode_index + 1; i < end_subnode_index; i++) {
						new_text += this.nodes[start_node_index].content[i].text
					}
					new_text += start_of_after_text
				}

				// Append new subnodes to node
				this.nodes[start_node_index].content = [
					...this.nodes[start_node_index].content.slice(0, start_subnode_index),
					subnode_before,
					{
						class: 'bold',
						text: new_text
					},
					subnode_after,
					...this.nodes[start_node_index].content.slice(end_subnode_index + 1),
				]
			}
		},

		insertNode(index) {
			this.lastID++
			this.nodes = [
				...this.nodes.slice(0, index + 1),
				{
					id: this.lastID,
					type: 'paragraph',
					text: ''
				},
				...this.nodes.slice(index + 1)
			]
		},

		splitNode(selection_info) {
			const {
				start_node_index,
				start_subnode_index,
				start_offset,
				start_text,
				end_node_index,
				end_subnode_index,
				end_offset,
				end_text
			} = selection_info

			if (start_node_index == end_node_index) {

				// Modify text in subnodes before and after split
				const subnode_before = {
					...this.nodes[start_node_index].content[start_subnode_index],
					text: start_text.slice(0, start_offset)
				}
				const subnode_after = {
					...this.nodes[start_node_index].content[end_subnode_index],
					text: end_text.slice(end_offset) || null
				}
				console.log(end_text.slice(end_offset))
				console.log(end_text.slice(end_offset).length)
				
				// Attach modified subnodes to nodes before and after split
				const node_before = {
					...this.nodes[start_node_index],
					content: [
						...this.nodes[start_node_index].content.slice(0, start_subnode_index),
						subnode_before
					]
				}
				this.lastID++
				const node_after = {
					...this.nodes[start_node_index],
					id: this.lastID,
					content: [
						subnode_after,
						...this.nodes[start_node_index].content.slice(end_subnode_index + 1)
					]
				}

				// Place new nodes back into array
				this.nodes = [
					...this.nodes.slice(0, start_node_index),
					node_before,
					node_after,
					...this.nodes.slice(start_node_index + 1)
				]
				console.log(JSON.parse(JSON.stringify(this.nodes)))
			}
		},

		nodeTypeToElement(type) {
			switch (type) {
				case 'paragraph':
					return 'p'
				case 'header':
					return 'h2'
				default:
					return 'span'
			}
		},

		setCursor(node_index, subnode_index, offset) {
			this.$nextTick().then(() => {
				const selection = window.getSelection()
				const node = document.getElementById('nodes').childNodes[node_index]
				console.log(node)
				if (!node) return
				const subnode = node.childNodes[subnode_index]
				console.log(subnode)
				if (!subnode) return
				const text = subnode.childNodes[0]
				console.log(text)
				if (!text) return
				selection.setBaseAndExtent(text, offset, text, offset)
				console.log(selection)
			})
			
			// const range = document.createRange()
			// range.selectNode()
			// selection.addRange(range)
		},

		deleteNode(index) {
			this.nodes.splice(index, 1)
		},

		onEditorInput(event) {
			const type = event.inputType
			console.log(type)

			switch (event.inputType) {
				case 'formatBold':
					// this.replaceSelectedBoldTags('span', 'bold')
			}

		},

		selection_and_range_methods() {
			const selection = window.getSelection()
			const range = selection.getRangeAt(0)

			// Move cursor to start or end of selection
			range.collapse(true)  // true = start, false = end

			// Copy all selection content to string
			const range_content = range.toString()

			// Must be within a text node! Surround with parent element
			const new_parent = document.createElement('p')
			range.surroundContents(new_parent)

			// Cut piece of document as HTML
			const fragment = range.extractContents()

			// Delete selection contents
			range.deleteContents()
		},

		selectionToBlock(tag, class_name) {
			const selection = window.getSelection()
			const range = selection.getRangeAt(0)

			// If no selection, select current node
			if (range.collapsed) {
				range.selectNode(selection.anchorNode)
			}

			// Get selection content
			const range_content = range.toString()

			// Delete content from document
			range.deleteContents()

			// Insert new block element and fill with selection content
			const new_node = document.createElement(tag)
			new_node.className = class_name
			new_node.innerHTML = range_content
			range.insertNode(new_node)

			// Set cursor to end of selection
			range.collapse(false)
		},

		replaceTagRecursive(node, tag, class_name) {
			for (const child of node.childNodes) {
				if (child.nodeName == 'B') {
					const span = document.createElement(tag)
					span.className = class_name
					span.innerHTML = child.innerHTML
					child.replaceWith(span)
				}
				this.replaceTagRecursive(child, tag, class_name)
			}
		},

		replaceSelectedBoldTags(tag, class_name) {
			const selection = window.getSelection()
			const range = selection.getRangeAt(0)

			// Start with common ancestor, replace b tags with span tags
			this.replaceTagRecursive(range.commonAncestorContainer, tag, class_name)
		},

		onKeyDown(event) {
			const { key, metaKey } = event

			if (!this.editing) return

			const selection_info = this.getSelectionInfo()
			
			if (key == '-') {
				event.preventDefault()
				event.stopPropagation()

				console.log(window.history)
				console.log(selection_info)
				this.selectionToBlock('p', 'node blockquote')
				// this.selectionToInline('p', 'node blockquote')
			}



			
			// if (key == 'Enter') {
			// 	event.preventDefault()
			// 	event.stopPropagation()
			// 	// this.insertNode(selection_info.start_node_index)
			// 	this.splitNode(selection_info)
			// 	this.setCursor(selection_info.start_node_index + 1, 0, 0)
			// }
			// else if (key == 'Backspace') {
			// 	if (selection_info.has_selection) {
			// 		event.preventDefault()
			// 		event.stopPropagation()
			// 		this.deleteSelection(selection_info)
			// 		console.log(selection_info)
			// 		// const node = document.getElementById('nodes').childNodes[selection_info.start_node_index]
			// 		this.setCursor(selection_info.start_node_index, selection_info.start_subnode_index, selection_info.start_offset)
			// 	}
			// }
			// else if (key == 'b' && metaKey) {
			// 	event.preventDefault()
			// 	event.stopPropagation()
			// 	this.boldSelection(selection_info)
			// 	this.updateUndoHistory()
			// }
			// else if (key == 's' && metaKey) {
			// 	event.preventDefault()
			// 	event.stopPropagation()
			// 	this.setCursor(document.getElementById('1').childNodes[1], 3)
			// }
			// else if (key == 'Alt') {
			// 	this.updateUndoHistory()
			// }
			// else if (key == '-') {
			// 	event.preventDefault()
			// 	event.stopPropagation()
			// 	this.undo()
			// }
			// else if (key == '=') {
			// 	event.preventDefault()
			// 	event.stopPropagation()
			// 	this.redo()
			// }
		}
	},

	mounted() {
		window.addEventListener('keydown', this.onKeyDown)

		document.getElementById('nodes').addEventListener('input', this.onEditorInput)
	}
}
</script>

<style>

.home {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 2rem;
	width: 100%;
	min-width: 600px;
	max-width: 900px;
}

.edit-toggle {
	&.on {
		background-color: #5ceda0;
	}
	&.off {
		background-color: #ed5c5c;
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

.bold {
	color: #ff768f;
	font-weight: 600;
}

.node-toolbar {
	position: absolute;
	top: 0;
	left: 50%;
	transform: translate(-50%, -100%);

	button {
		--button-size: 32px;
		width: var(--button-size);
		height: var(--button-size);
	}
}

span {
	min-height: 1.75rem;
}

</style>
