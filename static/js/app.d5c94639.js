(function(){"use strict";var e={5503:function(e,t,n){var o=n(2856),s=function(){var e=this,t=e._self._c;return t("div",{attrs:{id:"app"}},[t("router-view")],1)},i=[],d={name:"App",components:{}},r=d,a=n(1656),c=(0,a.A)(r,s,i,!1,null,null,null),l=c.exports,u=n(1594),h=function(){var e=this,t=e._self._c;return t("div",{staticClass:"home"},[t("h3",[e._v("Editor")]),t("br"),t("button",{class:"edit-toggle "+(e.editing?"on":"off"),on:{click:function(t){e.editing=!e.editing}}},[e._v(e._s(e.editing?"Editing On":"Editing Off"))]),t("button",{staticClass:"edit-toggle",on:{click:e.saveDocument}},[e._v("Save")]),t("br"),t("br"),t("br"),t("div",{attrs:{id:"nodes",contenteditable:e.editing}},[t("p",{staticClass:"node header"},[e._v("This is a header")]),e._m(0),t("p",{staticClass:"node blockquote"},[e._v("This is a blockquote")]),t("p",[e._v("Suscipit aliquam integer auctor mi nibh pretium ultrices ut, faucibus himenaeos nulla volutpat luctus nisi nullam consequat, rhoncus dui turpis dapibus litora tortor egestas. Duis magnis commodo conubia rutrum venenatis consequat leo cursus urna, massa aliquam donec sapien sociis maecenas pulvinar in nostra nisl, egestas libero phasellus sociosqu mattis neque vulputate a. Suspendisse nulla blandit vitae libero interdum ornare, fringilla varius tempor curabitur eu, praesent volutpat convallis dapibus tellus.")])])])},p=[function(){var e=this,t=e._self._c;return t("p",[e._v("This is "),t("span",{staticClass:"bold"},[e._v("highlighted")]),e._v(" text.")])}],f=(n(4114),{name:"Home",components:{},data(){return{editing:!0,selectedNode:{index:null,id:null},lastID:99,nodes:[{id:0,type:"header",content:[{text:"Introduction"}]},{id:1,type:"paragraph",content:[{text:"This is the "},{class:"bold",text:"first"},{text:" line."}]},{id:2,type:"blockquote",content:[{text:"This is a blockquote."}]},{id:3,type:"line"},{id:4,type:"paragraph",content:[{text:"Suscipit aliquam integer auctor mi nibh pretium ultrices ut, faucibus himenaeos nulla volutpat luctus nisi nullam consequat, rhoncus dui turpis dapibus litora tortor egestas. Duis magnis commodo conubia rutrum venenatis consequat leo cursus urna, massa aliquam donec sapien sociis maecenas pulvinar in nostra nisl, egestas libero phasellus sociosqu mattis neque vulputate a. Suspendisse nulla blandit vitae libero interdum ornare, fringilla varius tempor curabitur eu, praesent volutpat convallis dapibus tellus."}]}],undo_history:[],undo_step:1,max_undo_history:10}},methods:{api(e,t,n){fetch(`/${e}`,{method:t,headers:{"Content-Type":"application/json"},body:JSON.stringify(n)}).then((e=>e.ok?e.json():e)).then((e=>console.log(e)))},saveDocument(){this.api("save/asdfasdfas","POST",{document:document.getElementById("nodes").innerHTML})},updateUndoHistory(){this.undo_history.push(JSON.stringify(this.nodes)),this.undo_history=this.undo_history.slice(-this.max_undo_history),window.localStorage.setItem("undo_history",this.undo_history),console.log(this.undo_history)},undo(){this.undo_step<this.undo_history.length&&this.undo_step++;const e=-this.undo_step;this.nodes=JSON.parse(this.undo_history.slice(e).shift())},redo(){this.undo_step>1&&this.undo_step--;const e=-this.undo_step;this.nodes=JSON.parse(this.undo_history.slice(e).shift())},getSelectionInfo(){const e=window.getSelection();if(!e.baseNode||!e.extentNode)return{start_node_index:-1,start_offset:-1,start_node_content:"",end_node_index:-1,end_offset:-1,end_node_content:"",has_selection:!1};const t={node:e.baseNode,node_index:Array.prototype.indexOf.call(e.baseNode.parentElement.parentElement.children,e.baseNode.parentElement),subnode_index:Array.prototype.indexOf.call(e.baseNode.parentElement.children,e.baseNode),offset:e.baseOffset},n={node:e.extentNode,node_index:Array.prototype.indexOf.call(e.extentNode.parentElement.parentElement.children,e.extentNode.parentElement),subnode_index:Array.prototype.indexOf.call(e.extentNode.parentElement.children,e.extentNode),offset:e.extentOffset};let o=t.node_index<=n.node_index?{...t}:{...n},s=t.node_index<=n.node_index?{...n}:{...t};return t.node_index==n.node_index&&(t.subnode_index>n.subnode_index&&(o=n,s=t),t.subnode_index==n.subnode_index&&t.offset>n.offset&&(o.offset=n.offset,s.offset=t.offset)),{start_node:o.node,start_offset:o.offset,end_node:s.node,end_offset:s.offset,has_selection:e.baseNode!=e.extentNode||e.baseOffset!=e.extentOffset}},deleteSelection(e){const{start_node_index:t,start_subnode_index:n,start_offset:o,start_text:s,end_node_index:i,end_subnode_index:d,end_offset:r,end_text:a}=e,c=s.slice(0,o),l=a.slice(r);if(this.$set(this.nodes[t].content,n,{...this.nodes[t].content[n],text:c+l}),t!=i)this.nodes[t].content.splice(n+1,1/0),this.nodes[i].content.splice(0,d+1),this.nodes[t].content=[...this.nodes[t].content,...this.nodes[i].content],this.nodes.splice(t+1,i-t);else{if(n==d)return;this.nodes[t].content.splice(n+1,d)}},boldSelection(e){const{start_node_index:t,start_subnode_index:n,start_offset:o,start_text:s,end_node_index:i,end_subnode_index:d,end_offset:r,end_text:a}=e;if(t==i){const e={...this.nodes[t].content[n],text:s.slice(0,o)},i={...this.nodes[t].content[d],text:a.slice(r)};let c=s.slice(o,r);if(n!=d){const e=s.slice(o),i=a.slice(0,r);c=e;for(let o=n+1;o<d;o++)c+=this.nodes[t].content[o].text;c+=i}this.nodes[t].content=[...this.nodes[t].content.slice(0,n),e,{class:"bold",text:c},i,...this.nodes[t].content.slice(d+1)]}},insertNode(e){this.lastID++,this.nodes=[...this.nodes.slice(0,e+1),{id:this.lastID,type:"paragraph",text:""},...this.nodes.slice(e+1)]},splitNode(e){const{start_node_index:t,start_subnode_index:n,start_offset:o,start_text:s,end_node_index:i,end_subnode_index:d,end_offset:r,end_text:a}=e;if(t==i){const e={...this.nodes[t].content[n],text:s.slice(0,o)},i={...this.nodes[t].content[d],text:a.slice(r)||null};console.log(a.slice(r)),console.log(a.slice(r).length);const c={...this.nodes[t],content:[...this.nodes[t].content.slice(0,n),e]};this.lastID++;const l={...this.nodes[t],id:this.lastID,content:[i,...this.nodes[t].content.slice(d+1)]};this.nodes=[...this.nodes.slice(0,t),c,l,...this.nodes.slice(t+1)],console.log(JSON.parse(JSON.stringify(this.nodes)))}},nodeTypeToElement(e){switch(e){case"paragraph":return"p";case"header":return"h2";default:return"span"}},setCursor(e,t,n){this.$nextTick().then((()=>{const o=window.getSelection(),s=document.getElementById("nodes").childNodes[e];if(console.log(s),!s)return;const i=s.childNodes[t];if(console.log(i),!i)return;const d=i.childNodes[0];console.log(d),d&&(o.setBaseAndExtent(d,n,d,n),console.log(o))}))},deleteNode(e){this.nodes.splice(e,1)},onEditorInput(e){const t=e.inputType;switch(console.log(t),e.inputType){case"formatBold":}},selection_and_range_methods(){const e=window.getSelection(),t=e.getRangeAt(0);t.collapse(!0);t.toString();const n=document.createElement("p");t.surroundContents(n);t.extractContents();t.deleteContents()},selectionToBlock(e,t){const n=window.getSelection(),o=n.getRangeAt(0);o.collapsed&&o.selectNode(n.anchorNode);const s=o.toString();o.deleteContents();const i=document.createElement(e);i.className=t,i.innerHTML=s,o.insertNode(i),o.collapse(!1)},replaceTagRecursive(e,t,n){for(const o of e.childNodes){if("B"==o.nodeName){const e=document.createElement(t);e.className=n,e.innerHTML=o.innerHTML,o.replaceWith(e)}this.replaceTagRecursive(o,t,n)}},replaceSelectedBoldTags(e,t){const n=window.getSelection(),o=n.getRangeAt(0);this.replaceTagRecursive(o.commonAncestorContainer,e,t)},onKeyDown(e){const{key:t,metaKey:n}=e;if(!this.editing)return;const o=this.getSelectionInfo();"-"==t&&(e.preventDefault(),e.stopPropagation(),console.log(window.history),console.log(o),this.selectionToBlock("p","node blockquote"))}},mounted(){window.addEventListener("keydown",this.onKeyDown),document.getElementById("nodes").addEventListener("input",this.onEditorInput)}}),_=f,m=(0,a.A)(_,h,p,!1,null,null,null),g=m.exports;o.Ay.use(u.Ay);const x=[{path:"/",name:"home",component:g}],b=new u.Ay({routes:x});var v=b,y=n(1910);o.Ay.use(y.Ay);var N=new y.Ay.Store({state:{},getters:{},mutations:{},actions:{},modules:{}});o.Ay.config.productionTip=!1,new o.Ay({router:v,store:N,render:e=>e(l)}).$mount("#app")}},t={};function n(o){var s=t[o];if(void 0!==s)return s.exports;var i=t[o]={exports:{}};return e[o].call(i.exports,i,i.exports,n),i.exports}n.m=e,function(){var e=[];n.O=function(t,o,s,i){if(!o){var d=1/0;for(l=0;l<e.length;l++){o=e[l][0],s=e[l][1],i=e[l][2];for(var r=!0,a=0;a<o.length;a++)(!1&i||d>=i)&&Object.keys(n.O).every((function(e){return n.O[e](o[a])}))?o.splice(a--,1):(r=!1,i<d&&(d=i));if(r){e.splice(l--,1);var c=s();void 0!==c&&(t=c)}}return t}i=i||0;for(var l=e.length;l>0&&e[l-1][2]>i;l--)e[l]=e[l-1];e[l]=[o,s,i]}}(),function(){n.n=function(e){var t=e&&e.__esModule?function(){return e["default"]}:function(){return e};return n.d(t,{a:t}),t}}(),function(){n.d=function(e,t){for(var o in t)n.o(t,o)&&!n.o(e,o)&&Object.defineProperty(e,o,{enumerable:!0,get:t[o]})}}(),function(){n.g=function(){if("object"===typeof globalThis)return globalThis;try{return this||new Function("return this")()}catch(e){if("object"===typeof window)return window}}()}(),function(){n.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)}}(),function(){var e={524:0};n.O.j=function(t){return 0===e[t]};var t=function(t,o){var s,i,d=o[0],r=o[1],a=o[2],c=0;if(d.some((function(t){return 0!==e[t]}))){for(s in r)n.o(r,s)&&(n.m[s]=r[s]);if(a)var l=a(n)}for(t&&t(o);c<d.length;c++)i=d[c],n.o(e,i)&&e[i]&&e[i][0](),e[i]=0;return n.O(l)},o=self["webpackChunkclient"]=self["webpackChunkclient"]||[];o.forEach(t.bind(null,0)),o.push=t.bind(null,o.push.bind(o))}();var o=n.O(void 0,[504],(function(){return n(5503)}));o=n.O(o)})();
//# sourceMappingURL=app.d5c94639.js.map