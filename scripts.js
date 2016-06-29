slider('#en_slider', '#english_graph', english_all_links);
slider('#ru_slider', '#russian_graph', all_links);

$('#ru_slider').attr({"max": painters.length, "value": Math.round(painters.length/2)});
$('#en_slider').attr({"max": painters.length, "value": Math.round(painters.length/2)});

$('#ru_value').html(Math.round(painters.length/2));
$('#en_value').html(Math.round(painters.length/2));

var painters_number = document.getElementById('ru_slider').value;
var painters_to_keep = painters.slice(0, painters_number);
var old, links;
run_d3('#russian_graph', all_links);
run_d3('#english_graph', english_all_links);


function slider(slider_id, graph_id, links_object) {
$(slider_id).click(function() {
        old = painters_number;
        painters_number = this.value;
        $(slider_id + '+ div').html(Math.round(painters_number));
        if (old != painters_number) {
          painters_to_keep = painters.slice(0, painters_number);
          if (typeof force != 'undefined') {force.remove(); svg.remove}; 
          $(graph_id).html('');
          run_d3(graph_id, links_object);
        }
        
    });
}

function run_d3(placeholder, links_object) {
    console.log('call')
    console.log(painters_to_keep)
    links = [];
    for (var i=0; i < links_object.length; i++) {
        var source = links_object[i]['source'];
        var target = links_object[i]['target'];
        var weight = links_object[i]['weight'];
        console.log('object', links_object[i]);
        console.log('for loop', source, target);
        if (painters_to_keep.includes(source) &&  
            painters_to_keep.includes(target)) {
            console.log('Includes');
            links.push({"source":source, "target":target, "weight":weight});
      };
    };
    console.log(links);
    var nodes = {};
    if (force) {force.nodes = nodes}; 

    // Compute the distinct nodes from the links.
    links.forEach(function(link) {
      link.source = nodes[link.source] || (nodes[link.source] = {name: link.source});
      link.target = nodes[link.target] || (nodes[link.target] = {name: link.target});
    });


    var width = 1000,
        height = 1000;

    var force = d3.layout.force()
        .nodes(d3.values(nodes))
        .links(links)
        .size([width, height])
        .linkDistance(function(d) {
          return ((1/d.weight) / (Math.log(1/d.weight))) + 150;
        })
        .charge(-300)
        .on("tick", tick)
        .start();

    var svg = d3.select(placeholder).append("svg")
        .attr("width", width)
        .attr("height", height);

    // Per-type markers, as they don't inherit styles.
    svg.append("defs").selectAll("marker")
        .data(["suit", "licensing", "resolved"])
      .enter().append("marker")
        .attr("id", function(d) { return d; })
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 30)
        .attr("refY", -1.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
      .append("path")
        .attr("d", "M0,-5L10,0L0,5");

    var path = svg.append("g").selectAll("path")
        .data(force.links())
      .enter().append("path")
        .attr("class", function(d) { return "link " + d.type; })
        .attr("marker-end", function(d) { return "url(#" + d.type + ")"; });

    var circle = svg.append("g").selectAll("circle")
        .data(force.nodes())
      .enter().append("circle")
        .attr("r", 13)
        .call(force.drag);

    var text = svg.append("g").selectAll("text")
        .data(force.nodes())
      .enter().append("text")
        .attr("x", 8)
        .attr("y", ".31em")
        .text(function(d) { return d.name; });

    // Use elliptical arc path segments to doubly-encode directionality.
    function tick() {
      path.attr("d", linkArc);
      circle.attr("transform", transform);
      text.attr("transform", transform);
    }

    function linkArc(d) {
      var dx = d.target.x - d.source.x,
          dy = d.target.y - d.source.y,
          dr = Math.sqrt(dx * dx + dy * dy);
      return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
    }

    function transform(d) {
      return "translate(" + d.x + "," + d.y + ")";
    }

}

