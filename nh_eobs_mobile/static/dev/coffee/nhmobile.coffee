# NHMobile contains utilities for working with the nh_eobs_mobile controllers as well as AJAX
class NHMobile extends NHLib

 constructor: () ->
   @test = 'yo'
   
module?.exports.NHMobile = NHMobile
window?.NH = {}
window?.NH.NHMobile = NHMobile

