<template>
	<n-card v-if="matchList.length > 0" style="max-width: 1200px">
		<n-flex>
			<n-card
				v-for="match in matchList"
				:key="match.metadata.match_id"
				class="match"
				:title="match.metadata.map.name"
				style="cursor: pointer"
				hoverable
				@mousedown="
					() =>
						seekToGame(
							(new Date(match.metadata.started_at).getTime() -
								new Date(start).getTime()) /
								1000
						)
				"
			>
				<template #cover>
					<img :src="`http://localhost:3000/maps/${match.metadata.map.id}.jpg`" />
				</template>
				{{ match.metadata.queue.name }} <br />
				{{
					calcDuration(
						new Date(match.metadata.started_at).getTime() - new Date(start).getTime()
					)
				}}
				-
				{{
					calcDuration(
						new Date(match.metadata.started_at).getTime() +
							match.metadata.game_length_in_ms -
							new Date(start).getTime()
					)
				}}
			</n-card>
		</n-flex>
	</n-card>
</template>

<script setup lang="ts">
import { NCard, NFlex, NButton } from "naive-ui";
import { useAccount, usePlayer } from "~/store";

const accountStore = useAccount();
const player = usePlayer();

const start = computed(() => {
	return accountStore.matchList.start;
});

const matchList = computed(() => {
	return accountStore.matchList.matches.sort((a, b) => {
		return (
			new Date(a.metadata.started_at).getTime() - new Date(b.metadata.started_at).getTime()
		);
	});
});

const seekToGame = (time: number) => {
	player.YTplayer.seekTo(time, true);
};

const calcDuration = (_value: number) => {
	const value = Math.floor(_value / 1000);
	const hour = Math.floor(value / 3600);
	const minute = Math.floor((value % 3600) / 60);
	const second = Math.floor(value % 60);

	// prettier-ignore
	return `${hour.toString().padStart(2, "0")}:${minute.toString().padStart(2, "0")}:${second.toString().padStart(2, "0")}`;
};

onMounted(() => {
	// console.log(matchList.value);
	// console.log(matchList.value[0].metadata.started_at, start.value);
	// console.log(new Date(matchList.value[0].metadata.started_at), new Date(start.value));
});
</script>

<style>
.match {
	max-width: 300px;
}
</style>
