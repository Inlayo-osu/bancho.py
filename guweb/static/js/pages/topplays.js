new Vue({
    el: "#app",
    delimiters: ["<%", "%>"],
    data() {
        return {
            flags: window.flags || {},
            plays: [],
            mode: window.mode || 'std',
            mods: window.mods || 'vn',
            load: false,
            domain: window.domain || domain,
        };
    },
    created() {
        console.log('[TopPlays] Vue app created with:', {
            mode: this.mode,
            mods: this.mods,
            domain: this.domain
        });
        this.LoadTopPlays(this.mode, this.mods);
    },
    methods: {
        LoadTopPlays(newMode, newMods) {
            if (window.event)
                window.event.preventDefault();

            window.history.replaceState('', document.title, `/topplays?mode=${newMode}&mods=${newMods}`);
            this.$set(this, 'mode', newMode);
            this.$set(this, 'mods', newMods);
            this.$set(this, 'load', true);

            const gulagMode = this.StrtoGulagInt();
            const apiUrl = `${window.location.protocol}//api.${this.domain}/v1/get_top_plays`;
            console.log('[TopPlays] Loading top plays:', { mode: gulagMode, apiUrl });

            this.$axios.get(apiUrl, {
                params: {
                    mode: gulagMode,
                    limit: 100
                }
            }).then(res => {
                console.log('[TopPlays] Top plays loaded:', res.data);
                this.plays = res.data.plays || [];
                this.$set(this, 'load', false);
            }).catch(err => {
                console.error('[TopPlays] Failed to load top plays:', err);
                this.plays = [];
                this.$set(this, 'load', false);
            });
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
        },
        getDifficultyColor(diff) {
            if (diff < 2) return '#4FC0FF';
            if (diff < 2.7) return '#4FFFD5';
            if (diff < 4) return '#7CFF4F';
            if (diff < 5.3) return '#F6F05C';
            if (diff < 6.5) return '#FF8068';
            return '#FF4E6A';
        }
    }
});
