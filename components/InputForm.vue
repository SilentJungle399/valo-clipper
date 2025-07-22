<template>
	<div class="input-form">
		<div class="input-group">
			<span class="input-label">Youtube URL</span>
			<n-input-group>
				<n-input
					:style="{ width: '50rem' }"
					placeholder="https://youtube.com/..."
					v-model:value="data.youtubeUrl"
					@keydown.enter="handleYoutube"
				/>
				<n-button type="primary" @click="handleYoutube">
					<n-icon size="20">
						<Search />
					</n-icon>
				</n-button>
			</n-input-group>
		</div>
		<div class="input-group">
			<span class="input-label">Player Info</span>
			<n-input-group>
				<n-input
					:style="{ width: '10rem' }"
					placeholder="Player name"
					v-model:value="data.playerName"
					@keydown.enter="handlePlayerInfo"
				/>
				<n-input-group-label>#</n-input-group-label>
				<n-input
					:style="{ width: '5rem' }"
					placeholder="Tag"
					v-model:value="data.playerTag"
					@keydown.enter="handlePlayerInfo"
				/>
				<n-button type="primary" @click="handlePlayerInfo">
					<n-icon size="20">
						<Search />
					</n-icon>
				</n-button>
			</n-input-group>
		</div>
	</div>
</template>

<script setup lang="ts">
import { NInput, NInputGroup, NInputGroupLabel, NButton, NIcon, useMessage } from "naive-ui";
import { Search } from "@vicons/ionicons5";
import { usePlayer, useAccount } from "~/store";

const player = usePlayer();
const account = useAccount();
const message = useMessage();

const youtubeUrl = computed(() => player.youtubeUrl);
const name = computed(() => account.name);
const tag = computed(() => account.tag);

const data = reactive({
	youtubeUrl: "https://www.youtube.com/watch?v=eyNDCqcn3Z4",
	playerName: "the boeing",
	playerTag: "767",
});

const handleYoutube = () => {
	console.log(name.value, tag.value, youtubeUrl.value);
	if (!data.youtubeUrl) {
		message.error("Please enter a YouTube URL.");
		return;
	}
	message.success("YouTube URL submitted: " + data.youtubeUrl);
	player.loadVideoByUrl(data.youtubeUrl);

	if (name.value && tag.value) loadMatchesFromVideo();
};

const handlePlayerInfo = async () => {
	console.log(name.value, tag.value, youtubeUrl.value);
	if (!data.playerName || !data.playerTag) {
		message.error("Please enter both player name and tag.");
		return;
	} else if (
		data.playerName.length < 3 ||
		data.playerName.length > 16 ||
		data.playerTag.length < 3 ||
		data.playerTag.length > 5
	) {
		message.error("Please enter valid player info.");
		return;
	}

	account.setAccount({
		name: data.playerName,
		tag: data.playerTag,
	});

	if (youtubeUrl.value) loadMatchesFromVideo();
};

const loadMatchesFromVideo = async () => {
	const videoData: any = await $fetch("/api/youtube/info", {
		method: "GET",
		params: {
			url: youtubeUrl.value,
		},
	});

	if (videoData[1].type == "cached") {
		account.setMatchList(videoData[0]);
	} else {
		account.getMatchesByTime(
			new Date(videoData.release_timestamp * 1000).toISOString(),
			new Date(videoData.release_timestamp * 1000 + videoData.duration * 1000).toISOString(),
			youtubeUrl.value
		);
	}
};
</script>

<style>
.input-form {
	display: flex;
	gap: 10px;
}

.input-group {
	display: flex;
	flex-direction: column;
	gap: 2px;
}

.input-label {
	color: #9ca3af;
	font-weight: bold;
	font-size: 14px;
}
</style>
