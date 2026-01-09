new Vue({
    el: "#app",
    delimiters: ["<%", "%>"],
    data() {
        return {
            flags: window.flags,
            boards: [],
            mapinfo: {},
            mode: mode,
            mods: mods,
            load: false,
        };
    },
    created() {
        this.LoadBeatmap(mode, mods);
    },
    methods: {
        LoadBeatmap(newMode, newMods) {
            if (window.event)
                window.event.preventDefault();

            window.history.replaceState('', document.title, `/b/${bid}?mode=${newMode}&mods=${newMods}`);
            this.$set(this, 'mode', newMode);
            this.$set(this, 'mods', newMods);
            this.$set(this, 'load', true);

            const gulagMode = this.StrtoGulagInt();
            const apiUrl = `${window.location.protocol}//api.${domain}/v1/get_map_scores`;
            console.log('[Beatmap] Loading scores:', { bid, mode: gulagMode, apiUrl });

            this.$axios.get(apiUrl, {
                params: {
                    id: bid,
                    mode: gulagMode,
                    scope: 'best',
                    limit: 50
                }
            }).then(res => {
                console.log('[Beatmap] Scores loaded:', res.data);
                this.boards = res.data.scores || [];
                this.$set(this, 'load', false);
            }).catch(err => {
                console.error('[Beatmap] Failed to load beatmap scores:', err);
                this.boards = [];
                this.$set(this, 'load', false);
            });

            // Load map info
            const mapInfoUrl = `${window.location.protocol}//api.${domain}/v1/get_map_info`;
            console.log('[Beatmap] Loading map info:', { bid, mode: gulagMode, mapInfoUrl });

            this.$axios.get(mapInfoUrl, {
                params: {
                    id: bid,
                    mode: gulagMode
                }
            }).then(res => {
                console.log('[Beatmap] Map info loaded:', res.data);
                if (res.data.map) {
                    this.$set(this, 'mapinfo', res.data.map);
                }
            }).catch(err => {
                console.error('[Beatmap] Failed to load map info:', err);
            });
        },
        scoreFormat(score) {
            var addCommas = this.addCommas;
            if (score > 1000 * 1000) {
                if (score > 1000 * 1000 * 1000)
                    return `${addCommas((score / 1000000000).toFixed(2))} billion`;
                return `${addCommas((score / 1000000).toFixed(2))} million`;
            }
            return addCommas(score);
        },
        addCommas(nStr) {
            nStr += '';
            var x = nStr.split('.');
            var x1 = x[0];
            var x2 = x.length > 1 ? '.' + x[1] : '';
            var rgx = /(\d+)(\d{3})/;
            while (rgx.test(x1)) {
                x1 = x1.replace(rgx, '$1' + ',' + '$2');
            }
            return x1 + x2;
        },
        StrtoGulagInt() {
            switch (this.mode + "|" + this.mods) {
                case 'std|vn': return 0;
                case 'taiko|vn': return 1;
                case 'catch|vn': return 2;
                case 'mania|vn': return 3;
                case 'std|rx': return 4;
                case 'taiko|rx': return 5;
                case 'catch|rx': return 6;
                case 'std|ap': return 8;
                default: return 0;
            }
        },
        secondsToDhm(seconds) {
            seconds = Number(seconds);
            var h = Math.floor(seconds / 3600);
            var m = Math.floor(seconds % 3600 / 60);
            var s = Math.floor(seconds % 3600 % 60);

            var hDisplay = h > 0 ? h + ":" : "";
            var mDisplay = m > 0 ? (h > 0 && m < 10 ? "0" : "") + m + ":" : "0:";
            var sDisplay = (s < 10 ? "0" : "") + s;
            return hDisplay + mDisplay + sDisplay;
        },
        getScoreMods(modsInt) {
            if (!modsInt || modsInt === 0) return '';
            
            const modDict = {
                1: "NF", 2: "EZ", 4: "TD", 8: "HD",
                16: "HR", 32: "SD", 64: "DT", 128: "RX",
                256: "HT", 512: "NC", 1024: "FL", 2048: "AP",
                4096: "SO", 8192: "AP", 16384: "PF"
            };
            
            let mods = [];
            for (let [value, mod] of Object.entries(modDict)) {
                if (modsInt & parseInt(value)) {
                    mods.push(mod);
                }
            }
            
            let modsStr = mods.join('');
            modsStr = modsStr
                .replace('RXNC', 'NCRX')
                .replace('APNC', 'NCAP')
                .replace('DTNC', 'NC');
            
            return modsStr ? '+' + modsStr : '';
        },
        timeAgo(dateStr) {
            if (!dateStr) return 'Unknown';
            
            const date = new Date(dateStr + ' UTC');
            const now = new Date();
            const seconds = Math.floor((now - date) / 1000);
            
            if (seconds < 60) return 'just now';
            if (seconds < 3600) return Math.floor(seconds / 60) + 'm ago';
            if (seconds < 86400) return Math.floor(seconds / 3600) + 'h ago';
            if (seconds < 604800) return Math.floor(seconds / 86400) + 'd ago';
            if (seconds < 2592000) return Math.floor(seconds / 604800) + 'w ago';
            if (seconds < 31536000) return Math.floor(seconds / 2592000) + 'mo ago';
            return Math.floor(seconds / 31536000) + 'y ago';
        }
    }
});
