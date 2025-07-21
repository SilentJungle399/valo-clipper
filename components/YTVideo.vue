<template>
	<n-card class="video-container" :bordered="playerState === -1">
		<div class="placeholder" :style="{ display: playerState === -1 ? 'flex' : 'none' }">
			<n-icon size="80" color="#60a5fa" style="margin: 0 auto 10px auto">
				<LogoYoutube />
			</n-icon>
			<span style="font-weight: bold; font-size: 25px">Ready to Review</span>
			<span style="font-size: 14px; color: #9ca3af"
				>Enter a Youtube URL and your Valorant ID to start reviewing and clipping your
				VODs.</span
			>
		</div>
		<div id="player" style="display: none"></div>
	</n-card>
</template>

<script setup>
import { NCard, NIcon } from "naive-ui";
import { LogoYoutube } from "@vicons/ionicons5";
import { usePlayer } from "~/store";

const player = usePlayer();

const playerState = computed(() => player.state);

watch(
	() => playerState.value,
	(newState) => {
		const playerElement = document.getElementById("player");
		if (playerElement) {
			playerElement.style.display = newState === -1 ? "none" : "block";
		}
	},
	{ immediate: true }
);

const onYouTubeIframeAPIReady = () => {
	player.setYTplayer(
		// @ts-ignore
		new YT.Player("player", {
			height: "360",
			width: "640",
			playerVars: {
				playsinline: 1,
				autoplay: 0,
			},
			events: player.events,
		})
	);
};

onMounted(() => {
	// @ts-ignore
	window.onYouTubeIframeAPIReady = onYouTubeIframeAPIReady;

	const scriptTag = document.createElement("script");
	scriptTag.src = "https://www.youtube.com/iframe_api";
	const firstScriptTag = document.getElementsByTagName("script")[0];
	firstScriptTag.parentNode?.insertBefore(scriptTag, firstScriptTag);
});
</script>

<style>
.video-container {
	position: relative;
	width: 100%;
	padding-bottom: 56.25%;
	height: 0;
	overflow: hidden;
	background-color: #1e1e1e;
}

.video-container iframe {
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	border: 0;
}

.placeholder {
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	text-align: center;
	flex-direction: column;
	gap: 5px;
}
</style>
