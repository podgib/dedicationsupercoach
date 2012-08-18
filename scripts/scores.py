def batting_score(p):
  return p.runs+2*p.fours_hit+4*p.sixes_hit

def bowling_score(p,total_runs):
  if not p.bowled:
    return 0
  runs = p.runs_conceded
  if runs == 0:
    runs = 1
  economy = runs / (p.overs+p.balls/6.0)
  return total_runs/economy + 20*p.wickets + 10*p.maidens-5*p.wides-5*p.no_balls

def fielding_score(p):
  return 11-5*p.drops-5*p.non_attempts-3*p.diving_drops-2*p.misfields-p.other+3*p.catches+3*p.run_outs

def update_prices(p):
  games=p.playergame_set
  game_ids=[]
  bat=0
  bowl=0
  field=0
  game_count=0
  for g in games:
    bat += g.batting_points
    bowl += g.bowling_points
    field += g.fielding_points
    game_count+=1
  bat *= 1500
  bowl *= 1500
  field *= 1500

  bat += (5-game_count) * p.initial_batting_price
  bowl += (5-game_count) * p.initial_bowling_price
  field += (5-game_count) * p.initial_fielding_price

  p.batting_price=bat/5
  p.bowling_price=bowl/5
  p.fielding_price=field/5
