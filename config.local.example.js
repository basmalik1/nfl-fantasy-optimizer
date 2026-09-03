// Copy to config.local.js and fill in your league.
//   league -> the Sleeper URL: /leagues/<league_id>/...
//   draft  -> GET https://api.sleeper.app/v1/league/<league_id>  ->  "draft_id"
//   user   -> GET https://api.sleeper.app/v1/user/<your_username> ->  "user_id"
//   slot   -> your draft position (1 = first overall)
// Or skip this file and use URL params:
//   draft-assistant.html?draft=<draft_id>&slot=3&teams=10&rounds=15
//   season-manager.html?league=<league_id>&user=<user_id>
window.DRAFT_CONFIG = {
  name:          "My League",
  league:        "0000000000000000000",
  draft:         "0000000000000000000",
  user:          "0000000000000000000",
  teams:         10,
  slot:          1,
  rounds:        15,
  faab:          100,          // FAAB budget, if your league uses it
  waiverDay:     2,            // 0=Sun .. 2=Tue
  tradeDeadline: 11,
  starters:      { QB:1, RB:2, WR:2, TE:1, FLEX:2, K:1, DEF:1 }
};
