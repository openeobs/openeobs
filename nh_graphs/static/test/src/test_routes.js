var base_url = 'http://localhost:8069/mobile/';

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
                return _s('http',s)+base_url+r.url;
            },
            webSocketURL: function(s){
                return _s('ws',s)+base_url+r.url;
            }
        }
    }
    
   _nS('patient_list');
   _root.patient_list = function(){
	   return _wA({
		   method: 'GET',
		   url: base_url+'patients/'
	   })
   }
   
    _nS('single_patient');
   _root.single_patient = function(patient_id){
	   return _wA({
		   method: 'GET',
		   url: base_url+'patient/' + (function(k,v){ return v })('patient_id', patient_id)
	   })
   }
    
     _nS('json_patient_info');
   _root.json_patient_info = function(patient_id){
	   return _wA({
		   method: 'GET',
		   url: base_url+'patient/info/' + (function(k,v){ return v })('patient_id', patient_id)
	   })
   }
    
    _nS('task_list');
   _root.task_list = function(){
	   return _wA({
		   method: 'GET',
		   url: base_url+'tasks/'
	   })
   }
   
    _nS('single_task');
   _root.single_task = function(task_id){
	   return _wA({
		   method: 'GET',
		   url: base_url+'task/' + (function(k,v){ return v })('task_id', task_id)
	   })
   }

	 _nS('stylesheet');
   _root.stylesheet = function(){
	   return _wA({
		   method: 'GET',
		   url: base_url+'src/css/main.css'
	   })
   }
    
     _nS('js_routes');
   _root.js_routes = function(){
	   return _wA({
		   method: 'GET',
		   url: base_url+'src/js/routes.js'
	   })
   }
    
    _nS('observation_form_js');
   _root.observation_form_js = function(){
	   return _wA({
		   method: 'GET',
		   url: base_url+'src/js/observation.js'
	   })
   }
    
    _nS('observation_form_validation');
   _root.observation_form_validation = function(){
	   return _wA({
		   method: 'GET',
		   url: base_url+'src/js/validation.js'
	   })
   }
    
     _nS('data_driven_documents');
   _root.data_driven_documents = function(){
	   return _wA({
		   method: 'GET',
		   url: base_url+'src/js/d3.js'
	   })
   }
    
    _nS('patient_graph');
   _root.patient_graph = function(){
	   return _wA({
		   method: 'GET',
		   url: base_url+'src/js/draw_ews_graph.js'
	   })
   }
    
    _nS('graph_lib');
   _root.graph_lib = function(){
	   return _wA({
		   method: 'GET',
		   url: base_url+'src/js/graph_lib.js'
	   })
   }
    
    _nS('logo');
   _root.logo = function(){
	   return _wA({
		   method: 'GET',
		   url: base_url+'src/img/logo.png'
	   })
   }
    
     _nS('login');
   _root.login = function(){
	   return _wA({
		   method: 'GET',
		   url: base_url+'login/'
	   })
   }
    
    _nS('logout');
   _root.logout = function(){
	   return _wA({
		   method: 'GET',
		   url: base_url+'logout/'
	   })
   }
    
    _nS('task_form_action');
   _root.task_form_action = function(task_id){
	   return _wA({
		   method: 'POST',
		   url: base_url+'task/submit/' + (function(k,v){ return v })('task_id', task_id)
	   })
   }
   
   _nS('json_task_form_action');
   _root.json_task_form_action = function(observation, task_id){
	   return _wA({
		   method: 'POST',
		   url: base_url+'task/submit_ajax/' + (function(k,v){ return v })('observation', observation) + '/' + (function(k,v){ return v })('task_id', task_id)
	   })
   }
    
     _nS('patient_form_action');
   _root.patient_form_action = function(patient_id){
	   return _wA({
		   method: 'POST',
		   url: base_url+'patient/submit/' + (function(k,v){ return v })('patient_id', patient_id)
	   })
   }
     _nS('json_patient_form_action');
   _root.json_patient_form_action = function(observation, patient_id){
	   return _wA({
		   method: 'POST',
		   url: base_url+'patient/submit_ajax/' + (function(k,v){ return v })('observation', observation) + '/' + (function(k,v){ return v })('patient_id', patient_id)
	   })
   }
    
    _nS('calculate_obs_score');
   _root.calculate_obs_score = function(observation){
	   return _wA({
		   method: 'POST',
		   url: base_url+'observation/score/' + (function(k,v){ return v })('observation', observation)
	   })
   }
    
     _nS('json_take_task');
   _root.json_take_task = function(task_id){
	   return _wA({
		   method: 'POST',
		   url: base_url+'tasks/take_ajax/' + (function(k,v){ return v })('task_id', task_id)
	   })
   }
    
      _nS('json_cancel_take_task');
   _root.json_cancel_take_task = function(task_id){
	   return _wA({
		   method: 'POST',
		   url: base_url+'tasks/cancel_take_ajax/' + (function(k,v){ return v })('task_id', task_id)
	   })
   }
    
    _nS('json_partial_reasons');
   _root.json_partial_reasons = function(){
	   return _wA({
		   method: 'GET',
		   url: base_url+'ews/partial_reasons/'
	   })
   }
    
       _nS('confirm_clinical_notification');
   _root.confirm_clinical_notification = function(task_id){
	   return _wA({
		   method: 'POST',
		   url: base_url+'tasks/confirm_clinical/' + (function(k,v){ return v })('task_id', task_id)
	   })
   }
    
	     _nS('cancel_clinical_notification');
   _root.cancel_clinical_notification = function(task_id){
	   return _wA({
		   method: 'POST',
		   url: base_url+'tasks/cancel_clinical/' + (function(k,v){ return v })('task_id', task_id)
	   })
   }
    
    _nS('ajax_task_cancellation_options');
   _root.ajax_task_cancellation_options = function(){
	   return _wA({
		   method: 'GET',
		   url: base_url+'tasks/cancel_reasons/'
	   })
   }
   
    
    _nS('confirm_review_frequency');
   _root.confirm_review_frequency = function(task_id){
	   return _wA({
		   method: 'POST',
		   url: base_url+'tasks/confirm_review_frequency/' + (function(k,v){ return v })('task_id', task_id)
	   })
   }
    
     _nS('confirm_bed_placement');
   _root.confirm_bed_placement = function(task_id){
	   return _wA({
		   method: 'POST',
		   url: base_url+'tasks/confirm_bed_placement/' + (function(k,v){ return v })('task_id', task_id)
	   })
   }
    
      _nS('ajax_get_patient_obs');
   _root.ajax_get_patient_obs = function(patient_id){
	   return _wA({
		   method: 'GET',
		   url: base_url+'patient/ajax_obs/' + (function(k,v){ return v })('patient_id', patient_id)
	   })
   }
   
    
       _nS('patient_ob');
   _root.patient_ob = function(observation, patient_id){
	   return _wA({
		   method: 'GET',
		   url: base_url+'patient/observation/' + (function(k,v){ return v })('observation', observation) + '/' + (function(k,v){ return v })('patient_id', patient_id)
	   })
   }
    
      _nS('bristol_stools_chart');
   _root.bristol_stools_chart = function(){
	   return _wA({
		   method: 'GET',
		   url: base_url+'src/img/bristol_stools_chart.png'
	   })
   }
    
    

})(frontend_routes)