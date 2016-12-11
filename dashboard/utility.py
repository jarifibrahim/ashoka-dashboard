from .models import WeekWarning


def check_warnings(team):
    status = {
        'green': 'G',
        'yellow': 'Y',
        'red': 'R'
    }

    current_week = team.dashboard.current_week
    week_warning = WeekWarning.objects.get(week_number=current_week)
    tw = team.warnings

    # Total calls check
    def _total_calls_check():
        response_count = team.consultant_surveys.all().count()
        change_count = team.team_status.call_change_count
        total_call_count = response_count + change_count
        if total_call_count < week_warning.calls_red_warning:
            msg = "Total Calls ({0} + {1}): {2} < Expected Calls: {3}"
            msg.format(response_count, change_count, total_call_count,
                       week_warning.calls_red_warning)
            return status['red'], msg
        elif total_call_count < week_warning.calls_yellow_warning:
            return status['yellow'], ""
        else:
            return status['green'], ""

    # Current Phase
    def _phase_check():
        last_response = team.last_response
        # If there are no responses skip the following section
        if last_response:
            current_phase = last_response.current_phase.phase_number
            yellow = week_warning.phase_yellow_warning
            red = week_warning.phase_red_warning
            green = week_warning.phase
            if yellow:
                if yellow.phase_number == current_phase:
                    return status['yellow'], ""
            if green:
                if green.phase_number == current_phase:
                    return status['green'], ""
            if red:
                if red.phase_number < current_phase:
                    return status['red'], ""
        return status['green'], ""

    # Kick Off
    def _kick_off_check():
        if team.team_status.kick_off == "NS":
            yellow = week_warning.kick_off_yellow_warning
            red = week_warning.kick_off_red_warning
            if yellow:
                return status['yellow'], ""
            if red:
                return status['red'], ""
            return tw.kick_off, ""

    # Mid Term
    def _mid_term_check():
        if team.team_status.mid_term == "NS":
            yellow = week_warning.mid_term_yellow_warning
            red = week_warning.mid_term_red_warning
            if yellow:
                return status['yellow'], ""
            elif red:
                return status['red'], ""
        else:
            return status['green'], ""

    # Consultant Rating
    def _consultant_rating_check():
        c_last_rating = team.last_consultant_rating
        if c_last_rating:
            if c_last_rating < week_warning.consultant_rating_red_warning:
                return status['red'], ""
            else:
                return status['green'], ""
        # If there are no ratings
        else:
            return status['green'], ""

    # Fellow Rating
    def _fellow_rating_check():
        f_last_rating = team.last_fellow_rating
        if f_last_rating:
            if f_last_rating < week_warning.fellow_rating_red_warning:
                return status['red'], ""
            else:
                return status['green'], ""
        # If there are no ratings
        else:
            return status['green'], ""

    # Unprepared calls
    def _unprepared_calls_check():
        percentage = team.unprepared_calls_percentage
        if percentage:
            if percentage < week_warning.unprepared_calls_red_warning:
                return status['red'], ""
            elif percentage < week_warning.unprepared_calls_yellow_warning:
                return status['yellow'], ""
        return status['green'], ""

    tw.call_count, tw.call_count_comment = _total_calls_check()
    tw.phase, tw.phase_comment = _phase_check()
    tw.kick_off, tw.kick_off_comment = _kick_off_check()
    tw.mid_term, tw.mid_term_comment = _mid_term_check()
    tw.consultant_rating, tw.consultant_rating_comment = _consultant_rating_check()
    tw.fellow_rating, tw.fellow_rating_comment = _fellow_rating_check()
    tw.unprepared_calls, tw.unprepared_calls_comment = _unprepared_calls_check()
    tw.save()
