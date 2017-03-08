# NHMobilePatient contains utilities for working with
# the nh_eobs_mobile patient view, namely getting data
#  and passing it to graph lib
### istanbul ignore next ###
class NHMobilePatientMentalHealth extends NHMobilePatient

  constructor: () ->
    super(refused=true, partialType="character")

### istanbul ignore if ###
if !window.NH
  window.NH = {}
### istanbul ignore else ###
window?.NH.NHMobilePatient = NHMobilePatientMentalHealth