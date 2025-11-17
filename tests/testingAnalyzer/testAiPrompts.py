from analyzer import aiPrompts

def test_initial_prompt_includes_hint():
    hint = "DevOps Engineer"
    
    prompt = aiPrompts.get_initial_cv_analysis_prompt(
        cv_text="my cv",
        canonical_skills=[],
        canonical_levels=[],
        user_profiles=[],
        hint_preferred_profile=hint
    )
    
    assert "Profile Hint" in prompt
    assert "DevOps Engineer" in prompt

def test_initial_prompt_skips_none_hint():
    prompt = aiPrompts.get_initial_cv_analysis_prompt(
        cv_text="my cv",
        canonical_skills=[],
        canonical_levels=[],
        user_profiles=[],
        hint_preferred_profile=None
    )
    
    assert "Profile Hint" not in prompt

def test_initial_prompt_skips_unknown_hint():
    prompt = aiPrompts.get_initial_cv_analysis_prompt(
        cv_text="my cv",
        canonical_skills=[],
        canonical_levels=[],
        user_profiles=[],
        hint_preferred_profile="Unknown Tech Profile"
    )
    
    assert "Profile Hint" not in prompt

def test_summary_prompt_for_tech_profile():
    prompt = aiPrompts.get_summary_prompt(
        cv_text="my cv",
        user_profile="Full Stack Developer",
        cv_skills=["python"],
        user_level="1-2 שנים",
        smart_gaps=["react"]
    )
    
    assert "expert AI Career Advisor" in prompt
    assert "gap_analysis_intro" in prompt
    assert "Full Stack Developer" in prompt
    assert "react" in prompt

def test_summary_prompt_for_non_tech_profile():
    prompt = aiPrompts.get_summary_prompt(
        cv_text="my cv",
        user_profile="Not a Tech Profile",
        cv_skills=[],
        user_level="",
        smart_gaps=[]
    )
    
    assert "Return exactly the following JSON object" in prompt
    assert "פרופיל מקצועי שאינו בתחום ההייטק" in prompt

def test_summary_prompt_for_unknown_profile():
    prompt = aiPrompts.get_summary_prompt(
        cv_text="my cv",
        user_profile="Unknown Tech Profile",
        cv_skills=[],
        user_level="3-4 שנים",
        smart_gaps=[]
    )
    
    assert "Your *only* task is to return the following JSON object" in prompt
    assert "לא הצלחנו לזהות באופן אוטומטי" in prompt
    assert "3-4 שנים" in prompt