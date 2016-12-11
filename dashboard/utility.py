from .models import WeekWarning


class Warnings:
    @staticmethod
    def check_warnings(team):
        status = {
            'green': 'G',
            'yellow': 'Y',
            'red': 'R'
        }

        current_week = team.dashboard.current_week
        week_warning = WeekWarning.objects.get(week_number=current_week)
        team_warning = team.warnings

        # Total calls check
        def _total_calls_check():
            total_call_count = (team.consultant_surveys.all().count() +
                                team.team_status.call_change_count)
            if total_call_count < week_warning.calls_red_warning:
                return status['red']
            elif total_call_count < week_warning.calls_yellow_warning:
                return status['yellow']
            else:
                return status['green']

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
                        return status['yellow']
                if green:
                    if green.phase_number == current_phase:
                        return status['green']
                if red:
                    if red.phase_number < current_phase:
                        return status['red']
            return status['green']

        # Kick Off
        def _kick_off_check():
            if team.team_status.kick_off == "NS":
                yellow = week_warning.kick_off_yellow_warning
                red = week_warning.kick_off_red_warning
                if yellow:
                    return status['yellow']
                else:
                    return status['red']
            else:
                return status['green']

        # Mid Term
        def _mid_term_check():
            if team.team_status.mid_term == "NS":
                yellow = week_warning.mid_term_yellow_warning
                red = week_warning.mid_term_red_warning
                if yellow:
                    return status['yellow']
                elif red:
                    return status['red']
            else:
                return status['green']

        # Consultant Rating
        def _consultant_rating_check():
            c_last_rating = team.last_consultant_rating
            if c_last_rating:
                if c_last_rating < week_warning.consultant_rating_red_warning:
                    return status['red']
                else:
                    return status['green']
            # If there are no ratings
            else:
                return status['green']

        # Fellow Rating
        def _fellow_rating_check():
            f_last_rating = team.last_fellow_rating
            if f_last_rating:
                if f_last_rating < week_warning.fellow_rating_red_warning:
                    return status['red']
                else:
                    return status['green']
            # If there are no ratings
            else:
                return status['green']

        team_warning.call_count = _total_calls_check()
        team_warning.phase = _phase_check()
        team_warning.kick_off = _kick_off_check()
        team_warning.mid_term = _mid_term_check()
        team_warning.consultant_rating = _consultant_rating_check()
        team_warning.fellow_rating = _fellow_rating_check()
        team_warning.save()