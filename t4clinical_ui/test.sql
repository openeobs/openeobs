	with 
	max_sequence as(
        select 
            spell.id as spell_id,
			activity.data_model,
			activity.state,
			max(activity.sequence) as sequence
        from t4_clinical_spell spell
        inner join t4_activity activity on activity.patient_id = spell.patient_id
        group by spell_id, activity.data_model, activity.state
    ),
    spell_latest_activity as (
	    select 
	    	max_sequence.spell_id,
	    	activity.state,
	    	array_agg(activity.id) as ids
	    from t4_activity activity
	    inner join max_sequence on max_sequence.data_model = activity.data_model
	    	 and max_sequence.state = activity.state
	    	 and max_sequence.sequence = activity.sequence
	
		group by max_sequence.spell_id, activity.state
	)
	
	select 
		activity.spell_id,
		height.height,
		diabetes.diabetes,
		mrsa.mrsa,
		pbpm.pbp_monitoring,
		wm.weight_monitoring,
		o2target_level.id as o2target_level_id
		
	from spell_latest_activity activity
	left join t4_clinical_patient_observation_height height on activity.ids && array[height.activity_id]
	left join t4_clinical_patient_diabetes diabetes on activity.ids && array[diabetes.activity_id]
	left join t4_clinical_patient_pbp_monitoring pbpm on activity.ids && array[pbpm.activity_id]
	left join t4_clinical_patient_weight_monitoring wm on activity.ids && array[wm.activity_id]
	left join t4_clinical_patient_o2target o2target on activity.ids && array[o2target.activity_id]
	left join t4_clinical_o2level o2target_level on o2target_level.id = o2target.level_id
	left join t4_clinical_patient_mrsa mrsa on activity.ids && array[mrsa.activity_id]
	where activity.state = 'completed'