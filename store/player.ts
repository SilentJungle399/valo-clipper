import { defineStore } from "pinia";

export default defineStore("player", () => {
	const YTplayer = ref<any>(null);
	const state = ref(-1);

	const setYTplayer = (player: any) => {
		if (YTplayer.value) return;
		YTplayer.value = player;

		/* TODO - for external seekbar */
		// const seekbar = useSeekbar();
		// const queue = useQueue();
		// const current = computed(() => queue.current);
		// setInterval(() => {
		// 	if (YTplayer.value.getCurrentTime && current) {
		// 		const currentPos = YTplayer.value.getCurrentTime();
		// 		progress.value = currentPos;
		// 		const duration = YTplayer.value.getDuration();
		// 		seekbar.setProgress((currentPos / duration) * 100, true);
		// 	} else {
		// 		seekbar.setProgress(0, true);
		// 	}
		// }, 100);
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
		console.log(url);
		if (YTplayer.value && YTplayer.value.loadVideoByUrl) {
			YTplayer.value.loadVideoByUrl(
				`http://www.youtube.com/v/${url.split("?v=")[1]}?version=3&rel=0&modestbranding=1`
			);
		}
	};

	return {
		YTplayer,
		events,
		state,
		setYTplayer,
		loadVideoByUrl,
	};
});
