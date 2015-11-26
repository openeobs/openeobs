(function() {
    var expected_route_list = {{ route_name_list }};
    var actual_route_list = [{% for r in routes %}'{{ r.name }}',{% endfor %}];
    for (var i=0;i<expected_route_list.length;i++) {
        if (actual_route_list.indexOf(expected_route_list[i]) == -1) {
            console.log("Cannot found this expected route: " + expected_route_list[i]);
            console.log("error");
        }
    }
    console.log("ok");
})();
