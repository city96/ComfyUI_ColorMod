import { app } from "/scripts/app.js";

function getNamedWidget(node, name) {
	return node.widgets.find(function(w){return w.name == name})
}

function addCanvasWidget(node) {
	const canvas = document.createElement("canvas");
	canvas.width = 1000
	canvas.height = 400

	canvas.style.pointerEvents = "none"; 
	canvas.style.border = "1px solid " + LiteGraph.WIDGET_OUTLINE_COLOR
	canvas.style.backgroundColor = LiteGraph.WIDGET_BGCOLOR
	canvas.stcolor = app.canvas.default_connection_color_byType.IMAGE

	let opts = {
		getMinHeight() { return 100 },
		selectOn: [],
	}
	const widget = node.addDOMWidget("canvas", "CTYCanvas", canvas, opts);
	widget.canvas = canvas;
	return widget;
}

function drawCanvasInitial(ctx, width, height, pv_x=null, pv_y=null) {
	// clear
	ctx.clearRect(0, 0, width, height)
	if (pv_x && pv_y) {
		// set style
		ctx.beginPath()
		ctx.lineWidth = 5
		ctx.strokeStyle = "#444"
		// draw cross
		ctx.moveTo(0, pv_y)
		ctx.lineTo(width, pv_y)
		ctx.moveTo(pv_x, 0)
		ctx.lineTo(pv_x, height)
		ctx.stroke()
	}
}

function drawCanvasCMMove(node) {
	let move = getNamedWidget(node, "move").value
	let canvas = getNamedWidget(node, "canvas").canvas

	let ctx = canvas.getContext("2d")
	
	// Calc coords
	let width = canvas.width
	let height = canvas.height
	let offset = height * -move

	// clear
	drawCanvasInitial(ctx, width, height)
	// set style
	ctx.beginPath()
	ctx.lineWidth = 15
	ctx.strokeStyle = canvas.stcolor
	// draw lines
	ctx.moveTo(0, height + offset)  // start
	ctx.lineTo(width, offset)   // start -> end
	ctx.stroke()
}

function drawCanvasCMMovePivot(node) {
	let move = getNamedWidget(node, "move").value
	let pivot = getNamedWidget(node, "pivot").value
	let canvas = getNamedWidget(node, "canvas").canvas

	let ctx = canvas.getContext("2d")

	// Calc pivot coords
	let width = canvas.width
	let height = canvas.height
	let pv_x = width * pivot
	let pv_y = height * (1.0 - pivot) - (height * move)

	// clear
	drawCanvasInitial(ctx, width, height, pv_x, pv_y)
	// set style
	ctx.beginPath()
	ctx.lineWidth = 15
	ctx.strokeStyle = canvas.stcolor
	// draw lines
	ctx.moveTo(0, height)  // start
	ctx.lineTo(pv_x, pv_y) // start -> pivot
	ctx.lineTo(width, 0)   // pivot -> end
	ctx.stroke()
}

function drawCanvasCMEdges(node) {
	let low = getNamedWidget(node, "low").value
	let high = getNamedWidget(node, "high").value
	let pivot = getNamedWidget(node, "pivot").value
	let canvas = getNamedWidget(node, "canvas").canvas

	let ctx = canvas.getContext("2d")
	ctx.lineWidth = 15
	ctx.strokeStyle = canvas.stcolor

	// Calc pivot coords
	let width = canvas.width
	let height = canvas.height
	let pv_x = width * pivot
	let pv_y = height * (1.0 - pivot)

	// clear
	drawCanvasInitial(ctx, width, height, pv_x, pv_y)
	// set style
	ctx.beginPath()
	ctx.lineWidth = 15
	ctx.strokeStyle = canvas.stcolor
	// draw lines
	ctx.moveTo(0, height * low)            // start
	ctx.lineTo(pv_x, pv_y)                 // start -> pivot
	ctx.lineTo(width, height * (1.0-high)) // pivot -> end
	ctx.stroke()
}

app.registerExtension({
	name: "City96.ColorMod",
	nodeCreated(node, app) {
		if (node.__proto__.comfyClass == "ColorModMove") {
			var widget = addCanvasWidget(node)
			var refresh = function(v=null) { drawCanvasCMMove(node) }
			getNamedWidget(node, "move").callback = refresh
			setTimeout(refresh, 100);
		}
		if (node.__proto__.comfyClass == "ColorModPivot") {
			var widget = addCanvasWidget(node)
			var refresh = function(v=null) { drawCanvasCMMovePivot(node) }
			getNamedWidget(node, "move").callback = refresh
			getNamedWidget(node, "pivot").callback = refresh
			setTimeout(refresh, 100);
		}
		if (node.__proto__.comfyClass == "ColorModEdges") {
			var widget = addCanvasWidget(node)
			var refresh = function(v) { drawCanvasCMEdges(node) }
			getNamedWidget(node, "low").callback = refresh
			getNamedWidget(node, "high").callback = refresh
			getNamedWidget(node, "pivot").callback = refresh
			setTimeout(refresh, 100);
		}
		if (node.__proto__.comfyClass == "ColorModExposureFusion") {
			console.log(node)
		}
	}
})
