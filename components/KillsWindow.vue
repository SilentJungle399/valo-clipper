<template>
	<n-card v-if="currentMatch" style="max-width: 1200px">
		{{ calcDuration(progress * 1000) }} {{ progress * 1000 }} <br />
		{{
			calcDuration(
				new Date(currentMatch.metadata.started_at).getTime() -
					new Date(streamStart).getTime()
			)
		}}
		{{ new Date(currentMatch.metadata.started_at).getTime() - new Date(streamStart).getTime()
		}}<br />

		{{
			calcDuration(
				progress * 1000 -
					(new Date(currentMatch.metadata.started_at).getTime() -
						new Date(streamStart).getTime())
			)
		}}

		{{
			progress * 1000 -
			(new Date(currentMatch.metadata.started_at).getTime() - new Date(streamStart).getTime())
		}}
		<n-flex style="gap: 20px" vertical>
			<n-flex style="gap: 30px">
				<n-flex vertical>
					<span style="font-weight: bold; color: #9ca3af">Global time offset:</span>
					<n-input-number v-model:value="globalOffset" style="max-width: 150px" />
				</n-flex>
				<n-flex vertical>
					<span style="font-weight: bold; color: #9ca3af">Skip time offset:</span>
					<n-input-number v-model:value="skipOffset" style="max-width: 150px" />
				</n-flex>
			</n-flex>
			<n-flex>
				<n-button
					@click="() => seekToKill(previousKill + timeDiff + offset * 1000)"
					tertiary
				>
					Previous kill
				</n-button>
				<n-button
					@click="() => seekToKill(nextKill + timeDiff - skipOffset + offset * 1000)"
					tertiary
				>
					Next kill
				</n-button>
			</n-flex>
			<n-flex>
				<n-button
					v-for="kill in filterKills(currentMatch.kills)"
					:key="kill.time_in_match_in_ms"
					class="kill-button"
					@click="() => seekToKill(kill.time_in_match_in_ms + timeDiff + offset * 1000)"
					:type="nextKill === kill.time_in_match_in_ms ? 'primary' : 'default'"
					ghost
				>
					<!-- {{ kill.killer.name }} - -->
					{{ calcDuration(kill.time_in_match_in_ms + timeDiff + offset * 1000) }}
					{{ kill.round }}
				</n-button>
			</n-flex>
		</n-flex>
	</n-card>
</template>

<script setup lang="ts">
import { NCard, NFlex, NButton, NInputNumber } from "naive-ui";
import { useAccount, useSeekbar, usePlayer } from "~/store";

const accountStore = useAccount();
const seekbar = useSeekbar();
const player = usePlayer();

const currentMatch = ref();
const timeDiff = ref(0);

const globalOffset = ref(48.5);
const skipOffset = ref(3);
const offset = computed(() => globalOffset.value + skipOffset.value);

const progress = computed(() => seekbar.progress);
const streamStart = computed(() => accountStore.matchList.start);
const profile = computed(() => accountStore.profile);

const matchList = computed(() => {
	return accountStore.matchList.matches.sort((a, b) => {
		return (
			new Date(a.metadata.started_at).getTime() - new Date(b.metadata.started_at).getTime()
		);
	});
});

const nextKill = computed(() => {
	const kills = filterKills(currentMatch.value.kills);
	const ret = kills.filter((kill) => {
		return (
			kill.time_in_match_in_ms + timeDiff.value + offset.value * 1000 >= progress.value * 1000
		);
	});

	return ret.length > 0 ? ret[0].time_in_match_in_ms : null;
});

const previousKill = computed(() => {
	const kills = filterKills(currentMatch.value.kills);
	const ret = kills.filter((kill) => {
		return (
			kill.time_in_match_in_ms + timeDiff.value + offset.value * 1000 < progress.value * 1000
		);
	});

	if (ret.length >= 2) {
		// if last kill is less than 2 seconds before current time, return second last kill
		if (
			ret[ret.length - 1].time_in_match_in_ms + timeDiff.value + offset.value * 1000 >
			progress.value * 1000 - 2000
		) {
			return ret[ret.length - 2].time_in_match_in_ms;
		}
	}

	return ret.length > 0 ? ret[ret.length - 1].time_in_match_in_ms : null;
});

const seekToKill = (time: number) => {
	player.YTplayer.seekTo(time / 1000, true);
};

const filterKills = (kills: any[]) => {
	return kills.filter((kill) => kill.killer.puuid == profile.value.data.puuid);
};

watch(
	() => progress.value,
	(newProgress) => {
		currentMatch.value = matchList.value.find((match) => {
			const matchStart = new Date(match.metadata.started_at).getTime();
			const matchEnd = matchStart + match.metadata.game_length_in_ms;
			const streamTime = new Date(streamStart.value).getTime() + newProgress * 1000;
			const found = streamTime >= matchStart && streamTime <= matchEnd;
			if (found) {
				timeDiff.value = matchStart - new Date(streamStart.value).getTime();
			}
			return found;
		});
	},
	{ immediate: true }
);

watch(currentMatch, (newMatch) => {
	console.log(newMatch);
});

const calcDuration = (_value: number) => {
	const value = Math.floor(_value / 1000);
	const hour = Math.floor(value / 3600);
	const minute = Math.floor((value % 3600) / 60);
	const second = Math.floor(value % 60);
	const ms = Math.floor(_value % 1000);

	// prettier-ignore
	return `${hour.toString().padStart(2, "0")}:${minute.toString().padStart(2, "0")}:${second.toString().padStart(2, "0")}.${ms}`;
};
</script>

<style>
.match {
	max-width: 300px;
}
</style>
