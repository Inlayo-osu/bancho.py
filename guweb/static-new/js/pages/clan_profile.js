new Vue({
    el: "#app",
    delimiters: ["<%", "%>"],
    data() {
        return {
            data: {
                clan: clanInfo,
                members: clanMembers,
                stats: {
                    out: {
                        0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 8: {}
                    },
                    load: true
                },
                scores: {
                    best: {
                        out: [],
                        load: true,
                        more: {
                            limit: 10,
                            full: true,
                            total: 0
                        }
                    }
                }
            },
            mode: mode,
            mods: mods,
            modegulag: 0,
            clanid: clanid
        };
    },
    created() {
        this.applyQueryParams();
        this.modegulag = this.StrtoGulagInt();
        this.LoadClanStats();
        this.LoadClanScores();
    },
    methods: {
        countryToEmoji(code) {
            if (!code || code.length !== 2) return '1f3f3-fe0f';
            code = code.toUpperCase();
            const codePoints = [];
            for (let i = 0; i < code.length; i++) {
                const codePoint = (0x1F1E6 + code.charCodeAt(i) - 65).toString(16);
                codePoints.push(codePoint);
            }
            return codePoints.join('-');
        },
        applyQueryParams() {
            try {
                const params = new URLSearchParams(window.location.search);
                const modeParam = params.get('mode');
                const modsParam = params.get('mods');

                if (modeParam && ['std', 'taiko', 'catch', 'mania'].includes(modeParam)) {
                    this.mode = modeParam;
                }
                if (modsParam && ['vn', 'rx', 'ap'].includes(modsParam)) {
                    this.mods = modsParam;
                }

                // Validate combinations
                if (this.mode === 'mania' && this.mods !== 'vn') {
                    this.mods = 'vn';
                } else if ((this.mode === 'taiko' || this.mode === 'catch') && this.mods === 'ap') {
                    this.mods = 'vn';
                }

                this.syncUrlQuery();
            } catch (e) {
                console.error('Error applying query params:', e);
            }
        },
        syncUrlQuery() {
            const url = new URL(window.location.href);
            url.searchParams.set('mode', this.mode);
            url.searchParams.set('mods', this.mods);
            window.history.replaceState({}, '', url.toString());
        },
        LoadClanStats() {
            this.$set(this.data.stats, 'load', true);

            const params = {
                mode: this.modegulag
            };

            // Fetch clan member stats and aggregate
            this.$axios.get(`${window.location.protocol}//api.${domain}/v1/get_clan`, {
                params: { id: this.clanid }
            }).then(clanRes => {
                const members = clanRes.data.members || [];
                const owner = clanRes.data.owner;

                // Fetch stats for all members
                const memberPromises = [...members, owner].map(member =>
                    this.$axios.get(`${window.location.protocol}//api.${domain}/v1/get_player_info`, {
                        params: { id: member.id, scope: 'stats' }
                    }).catch(() => null)
                );

                Promise.all(memberPromises).then(responses => {
                    // Aggregate stats by mode
                    for (let modeKey = 0; modeKey <= 11; modeKey++) {
                        let totalPP = 0;
                        let totalRScore = 0;
                        let totalTScore = 0;
                        let totalPlays = 0;
                        let accSum = 0;
                        let accCount = 0;

                        responses.forEach(res => {
                            if (res && res.data && res.data.player && res.data.player.stats) {
                                const stats = res.data.player.stats;
                                const modeStats = stats.find(s => s.mode === modeKey);
                                if (modeStats && modeStats.pp > 0) {
                                    totalPP += modeStats.pp || 0;
                                    totalRScore += modeStats.rscore || 0;
                                    totalTScore += modeStats.tscore || 0;
                                    totalPlays += modeStats.plays || 0;
                                    if (modeStats.acc > 0) {
                                        accSum += modeStats.acc;
                                        accCount++;
                                    }
                                }
                            }
                        });

                        this.$set(this.data.stats.out, modeKey, {
                            total_pp: totalPP,
                            avg_pp: responses.length > 0 ? totalPP / responses.length : 0,
                            total_rscore: totalRScore,
                            total_tscore: totalTScore,
                            total_plays: totalPlays,
                            avg_acc: accCount > 0 ? accSum / accCount : 0
                        });
                    }

                    this.$set(this.data.stats, 'load', false);
                });
            }).catch(err => {
                console.error('Error loading clan stats:', err);
                this.$set(this.data.stats, 'load', false);
            });
        },
        LoadClanScores() {
            this.$set(this.data.scores.best, 'load', true);

            const params = {
                mode: this.modegulag,
                limit: this.data.scores.best.more.limit,
                sort: 'pp',
                scope: 'best'
            };

            // Fetch scores from all clan members
            this.$axios.get(`${window.location.protocol}//api.${domain}/v1/get_clan`, {
                params: { id: this.clanid }
            }).then(clanRes => {
                const members = clanRes.data.members || [];
                const owner = clanRes.data.owner;

                // Fetch scores for all members
                const scorePromises = [...members, owner].map(member =>
                    this.$axios.get(`${window.location.protocol}//api.${domain}/v1/get_player_scores`, {
                        params: {
                            id: member.id,
                            mode: this.modegulag,
                            scope: 'best',
                            limit: 5
                        }
                    }).then(res => {
                        if (res.data && res.data.scores) {
                            return res.data.scores.map(score => ({
                                ...score,
                                player_name: member.name,
                                userid: member.id
                            }));
                        }
                        return [];
                    }).catch(() => [])
                );

                Promise.all(scorePromises).then(allScores => {
                    // Flatten and sort all scores
                    const flatScores = allScores.flat();
                    flatScores.sort((a, b) => (b.pp || 0) - (a.pp || 0));

                    this.$set(this.data.scores.best, 'out', flatScores.slice(0, this.data.scores.best.more.limit));
                    this.$set(this.data.scores.best.more, 'total', flatScores.length);
                    this.$set(this.data.scores.best.more, 'full', flatScores.length <= this.data.scores.best.more.limit);
                    this.$set(this.data.scores.best, 'load', false);
                }).catch(err => {
                    console.error('Error loading clan scores:', err);
                    this.$set(this.data.scores.best, 'load', false);
                });
            }).catch(err => {
                console.error('Error fetching clan data:', err);
                this.$set(this.data.scores.best, 'load', false);
            });
        },
        AddLimit(type) {
            if (type === 'bestscore') {
                this.data.scores.best.more.limit += 10;
                this.LoadClanScores();
            }
        },
        ChangeModeMods(mode, mods) {
            if (window.event)
                window.event.preventDefault();

            // Validate combinations
            if (mode === 'mania' && mods !== 'vn') {
                return;
            }
            if ((mode === 'taiko' || mode === 'catch') && mods === 'ap') {
                return;
            }

            this.mode = mode;
            this.mods = mods;
            this.modegulag = this.StrtoGulagInt();
            this.syncUrlQuery();
            this.LoadClanStats();
            this.LoadClanScores();
        },
        addCommas(nStr) {
            nStr += "";
            var x = nStr.split(".");
            var x1 = x[0];
            var x2 = x.length > 1 ? "." + x[1] : "";
            var rgx = /(\d+)(\d{3})/;
            while (rgx.test(x1)) {
                x1 = x1.replace(rgx, "$1" + "," + "$2");
            }
            return x1 + x2;
        },
        secondsToDhm(seconds) {
            seconds = Number(seconds);
            var d = Math.floor(seconds / (3600 * 24));
            var h = Math.floor((seconds % (3600 * 24)) / 3600);
            var m = Math.floor((seconds % 3600) / 60);

            var dDisplay = d > 0 ? d + "d " : "";
            var hDisplay = h > 0 ? h + "h " : "";
            var mDisplay = m > 0 ? m + "m" : "";
            return dDisplay + hDisplay + mDisplay;
        },
        StrtoGulagInt() {
            const mode = this.mode;
            const mods = this.mods;
            return {
                'vn-std': 0,
                'vn-taiko': 1,
                'vn-catch': 2,
                'vn-mania': 3,
                'rx-std': 4,
                'rx-taiko': 5,
                'rx-catch': 6,
                'ap-std': 8
            }[`${mods}-${mode}`] || 0;
        },
        StrtoModeInt() {
            return { 'std': 0, 'taiko': 1, 'catch': 2, 'mania': 3 }[this.mode] || 0;
        }
    }
});
