var frontend_routes = {}; (function(_root){
    var _nS = function(c,f,b){
        var e=c.split(f||"."),g=b||_root,d,a;
        for(d=0,a=e.length;d<a;d++){
            g=g[e[d]]=g[e[d]]||{};
        }
        return g;
    }
    var _qS = function(items){
        var qs = '';
        for(var i=0;i<items.length;i++) {
            if(items[i]) qs += (qs ? '&' : '') + items[i]};
        return qs ? ('?' + qs) : '';
    }
    var _s = function(p,s){
        return p+((s===true||(s&&s.secure))?'s':'')+'://';
    }
    var _wA = function(r){
        return {ajax:function(c){
            c=c||{};
            c.url=r.url;
            c.type=r.method;
            return jQuery.ajax(c);
        },
            method:r.method,
            type:r.method,
            url:r.url,
            absoluteURL: function(s){
                return _s('http',s)+'{{ base_url }}'+r.url;
            },
            webSocketURL: function(s){
                return _s('ws',s)+'{{ base_url }}'+r.url;
            }
        }
    }
    {% for route in routes %}
        _nS('{{ route.name }}');
        _root.{{ route.name }} = function({% if route.args %}{{ route.args | join(', ') }}{% endif %}) {
            return _wA({
                method:"{{ route.methods.0 }}",
                url:"{{ base_url }}{% if route.url_prefix %}{{ route.url_prefix }}{% else %}{{ base_prefix }}{% endif %}"
                {% for comp in route.url_components %}
                       + '/'
                    {% if comp.type == 'string' %}
                        + '{{ comp.name }}'
                    {% endif %}
                    {% if comp.type == 'func' %}
                         + (function(k,v) {
                        return v
                       })( "{{ comp.name }}", {{ comp.name }})
                    {% endif %}
                {% endfor %}
            })
        }
    {% endfor %}
})(frontend_routes)