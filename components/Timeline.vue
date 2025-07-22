<template>
	<n-card>
		<n-slider
			:max="duration"
			v-model:value="seekbar.progress"
			:step="0.1"
			:disabled="playerState !== 1 && playerState !== 2"
			@dragstart="dragStart"
			@dragend="dragEnd"
			:format-tooltip="formatTooltip"
		>
			<!-- <template #thumb>
				<n-icon-wrapper :border-radius="12">
					<n-icon
						:size="24"
						:component="playerState === 1 ? PauseCircleOutline : PlayCircleOutline"
					/>
				</n-icon-wrapper>
			</template> -->
		</n-slider>
	</n-card>
</template>

<script setup lang="ts">
import { NSlider, NCard, NIcon, NIconWrapper } from "naive-ui";
import { PauseCircleOutline, PlayCircleOutline } from "@vicons/ionicons5";
import { usePlayer, useSeekbar } from "~/store";

const player = usePlayer();
const seekbar = useSeekbar();

const playerState = computed(() => player.state);
const duration = computed(() => player.duration);

const dragStart = () => {
	seekbar.setDragging(true);
};

const dragEnd = () => {
	if (player.YTplayer && player.YTplayer.seekTo) {
		player.YTplayer.seekTo(seekbar.progress, true);
	}
	seekbar.setDragging(false);
};

const formatTooltip = (value: number) => {
	const hour = Math.floor(value / 3600);
	const minute = Math.floor((value % 3600) / 60);
	const second = Math.floor(value % 60);

	// prettier-ignore
	return `${hour.toString().padStart(2, "0")}:${minute.toString().padStart(2, "0")}:${second.toString().padStart(2, "0")}`;
};
</script>
