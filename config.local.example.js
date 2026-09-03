// Copy to config.local.js and fill in your league.
//   league id -> the Sleeper URL: /leagues/<league_id>/...
//   draft id  -> GET https://api.sleeper.app/v1/league/<league_id>  ->  "draft_id"
//   slot      -> your draft position (1 = first overall)
// Or skip this file entirely and use URL params:
//   ?draft=<draft_id>&slot=3&teams=10&rounds=15
window.DRAFT_CONFIG = {
  name:    "My League",
  draft:   "0000000000000000000",
  teams:   10,
  slot:    1,
  rounds:  15,
  starters:{ QB:1, RB:2, WR:2, TE:1, FLEX:2, K:1, DEF:1 }
};
