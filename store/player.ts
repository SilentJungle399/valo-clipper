import { defineStore } from "pinia";
import { useSeekbar, useAccount } from ".";

export default defineStore("player", () => {
	const YTplayer = ref<any>(null);
	const state = ref(-1);
	const duration = ref(0);
	const youtubeUrl = ref("");

	const setYTplayer = (player: any) => {
		if (YTplayer.value) return;
		YTplayer.value = player;

		const seekbar = useSeekbar();
		setInterval(() => {
			if (YTplayer.value.getCurrentTime && [1, 2, 3].includes(state.value)) {
				const currentPos = YTplayer.value.getCurrentTime();
				duration.value = YTplayer.value.getDuration();
				seekbar.setProgress(currentPos, true);
			} else {
				seekbar.setProgress(0, true);
			}
		}, 100);
	};

	const events = {
		onStateChange: (event: any) => {
			// -1 (unstarted)
			// 0 (ended)
			// 1 (playing)
			// 2 (paused)
			// 3 (buffering)
			// 5 (video cued)

			console.log("Player state changed:", event.data);
			state.value = event.data;
		},
		onReady: (event: any) => {
			console.log("Player is ready");
		},
		onError: (event: any) => {
			console.error("Error occurred in player:", event.data);
		},
	};

	const loadVideoByUrl = (url: string) => {
		if (YTplayer.value && YTplayer.value.loadVideoByUrl) {
			YTplayer.value.loadVideoByUrl(
				`http://www.youtube.com/v/${url.split("?v=")[1]}?version=3&rel=0&modestbranding=1`
			);
			youtubeUrl.value = url;
		}
	};

	return {
		YTplayer,
		events,
		state,
		duration,
		youtubeUrl,
		setYTplayer,
		loadVideoByUrl,
	};
});
