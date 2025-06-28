<template>
  <div class="home">

	<br>
	<br>


	<div :class="`document-panel ${is_document_panel_open ? 'open' : ''}`">
		<span class="documents-title">Documents</span>
		<button
			@click="newDocument()"
		>New</button>
		<br>
		<div
			v-for="document in Object.values(documents)"
			class="document"
			@click="fetchDocument(document.id)"
		>
			<p>{{ document.title || '(Untitled)' }}</p>
		</div>
	</div>

	<div class="toolbar">
		<button
			@click="is_document_panel_open = !is_document_panel_open"
		>Documents</button>
		<button
			@click="editing = !editing"
			:class="`edit-toggle ${editing ? 'on' : 'off'}`"
		>{{ editing ? 'Editing On' : 'Editing Off' }}</button>
		<button
			@click="() => apply_to_selected_nodes('h1', '', null)"
		>H1</button>
		<button
			@click="() => apply_to_selected_nodes('h2', '', null)"
		>H2</button>
		<button
			@click="() => apply_to_selected_nodes('h3', '', null)"
		>H3</button>
		<button
			@click="() => apply_to_selected_nodes('h4', '', null)"
		>H4</button>
		<button
			@click="() => apply_to_selected_nodes('p', '', null)"
		>P</button>
		<button
			@click="() => apply_to_selected_nodes('li', '', 'ul')"
		>B</button>
		<button
			@click="() => test()"
		>Test</button>
		<button
			@click="() => selectionToNode('p', 'node blockquote', null)"
		>Q</button>
	</div>

	<div class="save-indicator">
		<div v-if="save_status == 'pending'" class="saving pending">
			<div class="saving-loader"></div>
			<span>Saving...</span>
		</div>
		<div v-else-if="save_status == 'success'" class="saving">
			<span>Last Saved: {{ last_saved }}.</span>
		</div>
		<div v-else-if="save_status == 'error'" class="saving error">
			<span>Connection Error.</span>
		</div>
	</div>

	<div id="nodes" :contenteditable="editing">
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
import api from '@/api'

export default {
  name: 'Home',

  components: {
  },

	data() {
		return {
			editing: false,
			undo_history: [],
			undo_step: 1,
			max_undo_history: 10,
			debounce_timepoint: null,
			DEBOUNCE_TIME: 1000,
			last_saved: null,
			save_status: '',
			documents: {},
			current_document_id: null,
			is_document_panel_open: false
		}
	},

	methods: {
		debounce() {
			this.debounce_timepoint = Date.now()
			return new Promise((resolve, reject) => {
				window.setTimeout(() => {
					if (Date.now() > this.debounce_timepoint + this.DEBOUNCE_TIME) {
						resolve(true)
					}
				}, this.DEBOUNCE_TIME)
			})
		},

		test() {
			api(`http://127.0.0.1:5000/test/`, 'POST', {}).then(response => {
				console.log(response)
			})
		},

		saveDocument() {
			this.save_status = 'pending'
			api(`http://127.0.0.1:5000/save/${this.current_document_id}`, 'POST', {
				document: document.getElementById('nodes').innerHTML
			}).then(response => {
				window.setTimeout(() => {
					this.save_status = response.ok ? 'success' : 'error'
					this.last_saved = response.last_saved || ''
				}, 200)
			}).then(() => {
				this.fetchAllDocuments()
			})
		},

		fetchDocument(id) {
			api(`http://127.0.0.1:5000/fetch/${id}`, 'POST', {}).then(response => {
				console.log(response)
				if (response.ok) {
					document.getElementById('nodes').innerHTML = response.document
					this.save_status = 'success'
					this.last_saved = response.last_saved || ''
					this.is_document_panel_open = false
					this.editing = false
					this.current_document_id = id
					window.localStorage.setItem('current_document_id', id)
				}
				else {
					this.save_status = 'error'
				}
			})
		},

		fetchAllDocuments() {
			api(`http://127.0.0.1:5000/fetch_all`, 'POST', {}).then(response => {
				console.log(response)
				this.documents = response.documents || {}
			})
		},

		newDocument() {
			api(`http://127.0.0.1:5000/new`, 'POST', {}).then(response => {
				console.log(response)
				this.current_document_id = response.id || null
				this.save_status = response.ok ? 'success' : 'error'
				this.last_saved = response.last_saved || ''
				this.is_document_panel_open = false
				window.localStorage.setItem('current_document_id', response.id)
				this.fetchAllDocuments()
				this.fetchDocument(response.id)
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

		_splitNode(selection_info) {
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

			this.debounce().then(() => {
				this.saveDocument()
			})
		},

		selection_and_range_methods() {
			const selection = window.getSelection()
			const range = selection.getRangeAt(0)
			const node = document.getElementById('nodes')

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

			// Merge adjacent text nodes, remove empty nodes
			node.normalize()
		},

		splitNodeAtSelection() {
			const selection = window.getSelection()
			const base = selection.baseNode
			const extent = selection.extentNode
			const range = selection.getRangeAt(0)
			const common_ancestor = range.commonAncestorContainer

			// Get tag and class of current node
			const node_type = common_ancestor.nodeName
			const node_class = common_ancestor.className

			// Take contents of selection
			const contents = range.extractContents()

			// Split text node, base remains as first node
			base.splitText(selection.baseOffset)

			// Move newly created second text node into a brand new node
			const new_split_node = document.createElement(node_type)
			new_split_node.className = node_class
			new_split_node.appendChild(base.nextSibling)
			
			// Insert after original node
			base.parentNode.parentNode.insertBefore(new_split_node, base.parentNode.nextSibling)
			
			// Move extracted selection contents into another brand new node
			const new_selection_node = document.createElement(node_type)
			new_selection_node.className = node_class
			new_selection_node.appendChild(contents)

			// Insert after original node, placing in between original and split nodes
			base.parentNode.parentNode.insertBefore(new_selection_node, base.parentNode.nextSibling)
		},

		splitSelectionWithinNode() {
			const contents = range.extractContents()
			range.insertNode(contents)
		},

		get_parent_node(node) {
			const node_root = document.getElementById('nodes')
			for (const child of node_root.childNodes) {
				if (child.contains(node)) return child
			}
		},

		get_sub_parent_node(node) {
			const node_root = document.getElementById('nodes')
			for (const child of node_root.childNodes) {
				if (child.contains(node) && child.hasChildNodes()) {
					for (const grandchild of child.childNodes) {
						if (grandchild.contains(node)) return grandchild
					}
				}
			}
		},

		get_list_parent_node(node, root) {
			if (!root?.hasChildNodes()) return null
			for (const child of root.childNodes) {
				// If node is inside child, search further
				if (child.contains(node)) {
					// If node is list item, we found it
					if (this.is_list_node(child)) return child
					// Otherwise keep searching recursively on children
					const matched = this.get_list_parent_node(node, child)
					// If recursive search finds a match, return immediately
					if (matched) return matched
				}
			}
			return null
		},

		is_list_node(node) {
			return node?.nodeName == 'LI'
		},

		is_list_container_node(node) {
			return node?.nodeName == 'UL' || node?.nodeName == 'OL'
		},

		get_sorted_selection_nodes() {
			const selection = window.getSelection()
			const extent_compared_to_base = selection.baseNode.compareDocumentPosition(selection.extentNode)

			// extent is before, base is after
			if (extent_compared_to_base & Node.DOCUMENT_POSITION_PRECEDING) {
				return {
					start: selection.extentNode,
					end: selection.baseNode
				}
			}

			// base is before, extent is after
			// or same
			else {
				return {
					start: selection.baseNode,
					end: selection.extentNode
				}
			}
		},

		get_all_selected_nodes() {
			// Get properly aligned base and extent selection nodes
			const selected_nodes = this.get_sorted_selection_nodes()

			// If start or end direct parent is a list container, get the individual list item
			let start_parent = this.get_parent_node(selected_nodes.start)
			if (this.is_list_container_node(start_parent)) start_parent = this.get_list_parent_node(selected_nodes.start, document.getElementById('nodes'))
			let end_parent = this.get_parent_node(selected_nodes.end)
			if (this.is_list_container_node(end_parent)) end_parent = this.get_list_parent_node(selected_nodes.end, document.getElementById('nodes'))

			// If start and end are same node, return it
			if (start_parent.isSameNode(end_parent)) {
				return [start_parent]
			}

			// Search both direct parents and list items until no next sibling or matches end
			let nodes = []
			let current_node = start_parent
			while (current_node && current_node != end_parent) {
				nodes.push(current_node)
				// If <ul> or <ol> and has children, investigate children for matching <li>
				if (this.is_list_container_node(current_node.nextSibling) && current_node.nextSibling.hasChildNodes()) {
					current_node = current_node.nextSibling.childNodes[0]
				}
				// If <li> and no next sibling, go up to parent's next sibling
				else if (this.is_list_node(current_node) && !current_node.nextSibling) {
					current_node = current_node.parentNode.nextSibling
				}
				// Otherwise, continue search with next sibling
				else {
					current_node = current_node.nextSibling
				}
			}
			nodes.push(end_parent)

			// Return combination of all direct parents and list items from start to end
			return nodes
		},

		replace_single_node_tag(node, tag, class_name, outer_tag) {
			// Ignore list nodes
			if (this.is_list_node(node)) return

			// Select and extract node contents
			const range = document.createRange()
			range.selectNodeContents(node)
			const contents = range.extractContents()

			// Place contents of node into new tag
			let new_node = document.createElement(tag)
			new_node.className = class_name
			new_node.append(contents)
			if (outer_tag) {
				const outer_node = document.createElement(outer_tag)
				outer_node.append(new_node)
				new_node = outer_node
			}

			// Insert new node before original & delete original
			node.parentNode.insertBefore(new_node, node)
			node.parentNode.removeChild(node)
		},

		replace_list_node_tag(node, tag, class_name, outer_tag) {
			// Ignore non-list nodes
			// if (!this.is_list_node(node)) return
			console.log(node)
			return

			// Select and extract node contents
			window.getSelection().removeAllRanges()
			const range = document.createRange()
			range.selectNodeContents(node)
			const contents = range.extractContents()
			node.innerHTML = 'a'

			// Add range to selection
			window.getSelection().addRange(range)

			// After outdentation, this creates a <span> and a <br>
			// <ul>        ->     <span>
			//     <li>           <br>
			// Any list items before and after will be split into separate <ul> or <ol> tags

			// Outdent until node is no longer an <li> node (we've reached root nodes container)
			// Note: could be multiple nested <ul> or <ol> for indented lists
			let current_node = node
			console.log('before while', current_node)
			while (current_node?.parentNode && this.is_list_container_node(current_node.parentNode)) {
				document.execCommand('outdent', false, null)
				current_node = this. get_list_parent_node(window.getSelection().baseNode, document.getElementById('nodes'))
				console.log(current_node)
			}
			// current_node is now null

			// Get temporary <span> node
			const placement_node = this.get_parent_node(window.getSelection().baseNode)

			// Place contents of original node into new tag
			const new_node = document.createElement(tag)
			new_node.className = class_name
			new_node.append(contents)

			// Insert contents here before temporary <span> node
			const nodes_root = document.getElementById('nodes')
			nodes_root.insertBefore(new_node, placement_node)

			// Delete temporary span node and subsequent <br> node
			// if (placement_node.nextSibling) nodes_root.removeChild(placement_node.nextSibling)
			// nodes_root.removeChild(placement_node)
		},

		apply_to_selected_nodes(tag, class_name, outer_tag) {
			const all_selected_nodes = this.get_all_selected_nodes()

			// TO FIX: problems with above function this.get_all_selected_nodes() when 2 ul's next to each other

			for (const node of all_selected_nodes) {

				// If list node
				if (this.is_list_node(node)) {
					console.log('list node')
					this.replace_list_node_tag(node, tag, class_name, outer_tag)
				}
				
				// If non-list node (direct parent)
				else {
					console.log('non list node')
					this.replace_single_node_tag(node, tag, class_name, outer_tag)
				}
			}
		},

		selectionToNode(tag, class_name, wrapped_tag) {
			if (!this.editing) return

			let selection = window.getSelection()
			let range = selection.getRangeAt(0)
			let no_selection = range.collapsed
			let base_parent_node = this.get_parent_node(selection.baseNode)
			let extent_parent_node = this.get_parent_node(selection.extentNode)

			const is_list = this.is_list_node(base_parent_node) || this.is_list_node(extent_parent_node)

			// If selection is within same parent node, and node is already desired node type, do nothing
			if (base_parent_node.isSameNode(extent_parent_node)) {
				if (base_parent_node.nodeName == tag && base_parent_node.className == class_name) {
					return
				}
			}

			// If no selection, select entire node
			if (no_selection) {
				if (is_list) {
					const sub_parent = this.get_sub_parent_node(selection.baseNode)
					range.selectNodeContents(sub_parent)
				}
				else {
					range.selectNodeContents(base_parent_node)
				}
			}

			// If inside list (ul or ol), outdent it back to root node container
			// Then reapply function to properly convert to desired tag
			if (is_list) {
				document.execCommand('outdent', false, null)
				selection = window.getSelection()
				range = selection.getRangeAt(0)
				no_selection = true
				range.selectNodeContents(selection.baseNode)
				
				// Delete <br> created after conversion to span
				const next_node = selection.baseNode.parentNode.nextSibling
				if (next_node.nodeName == 'BR') {
					next_node.parentNode.removeChild(next_node)
				}
			}
			
			// Cut contents of selection
			const contents = range.extractContents()
			
			// Split node at collapsed selection point if there was a selection
			if (!no_selection) {
				document.execCommand('insertParagraph', false, null)
			}

			// Take parent of newly collapsed selection
			let parent_node = this.get_parent_node(window.getSelection().baseNode)
			
			// Create new node and insert extracted contents into it
			let new_node
			if (wrapped_tag) {
				new_node = document.createElement(wrapped_tag)
				new_node.className = class_name
				const new_inner_node = document.createElement(tag)
				new_inner_node.append(contents.textContent)
				new_node.append(new_inner_node)
			}
			else {
				new_node = document.createElement(tag)
				new_node.className = class_name
				new_node.append(contents.textContent)
			}
			
			// Insert between split nodes if using newly created node
			parent_node.parentNode.insertBefore(new_node, parent_node)
			
			// If there was no selection, we've extracted all contents and are left with empty parent node, delete it
			if (no_selection) {
				parent_node.parentNode.removeChild(parent_node)
			}

			// Set selection
			window.getSelection().getRangeAt(0).setStart(new_node, 0)
			window.getSelection().getRangeAt(0).setEnd(new_node, 0)
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
			const { key, metaKey, shiftKey, ctrlKey, altKey } = event

			if (!this.editing) return

			const selection_info = this.getSelectionInfo()

			if (key == 'Tab') {
				event.preventDefault()
				event.stopPropagation()
				document.execCommand(shiftKey ? 'outdent' : 'indent', false, null)
			}
			
			// if (key == '-') {
			// 	event.preventDefault()
			// 	event.stopPropagation()

			// 	console.log(window.history)
			// 	console.log(selection_info)
			// 	this.selectionToNode('p', 'node blockquote')
			// 	// this.selectionToInline('p', 'node blockquote')
			// }



			
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

		const current_document_id = window.localStorage.getItem('current_document_id')
		if (current_document_id) {
			this.current_document_id = current_document_id
			this.fetchDocument(current_document_id)
		}
	},

	created() {
		this.fetchAllDocuments()
	}
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
