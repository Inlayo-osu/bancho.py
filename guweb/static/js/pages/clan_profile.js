new Vue({
    el: "#app",
    delimiters: ["<%", "%>"],
    data() {
        return {
            data: {
                clan: clanInfo,
                members: clanMembers,
                stats: {
                    totalPP: 0,
                    totalScore: 0,
                    avgPP: 0,
                    avgAcc: 0,
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
            
            // Calculate stats from members
            let totalPP = 0;
            let totalScore = 0;
            let totalAcc = 0;
            let memberCount = this.data.members.length;
            
            // This is a simplified version - in production you'd fetch this from API
            this.$set(this.data.stats, 'load', false);
        },
        LoadClanScores() {
            this.$set(this.data.scores.best, 'load', true);
            
            const params = {
                clan_id: this.clanid,
                mode: this.StrtoGulagInt(),
                limit: this.data.scores.best.more.limit,
                sort: 'pp'
            };

            // Since there's no clan scores API yet, we'll just show member list
            // In production, you would call: this.$axios.get(`${window.location.protocol}//api.${domain}/v1/get_clan_scores`, { params })
            
            this.$set(this.data.scores.best, 'load', false);
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
