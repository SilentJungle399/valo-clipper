<template>
	<n-card v-if="currentMatch" style="max-width: 1200px">
		<n-flex style="gap: 20px" vertical>
			<n-flex>
				<n-button
					@click="() => seekToKill(previousKill + timeDiff + offset * 1000)"
					tertiary
				>
					Previous kill
				</n-button>
				<n-button @click="() => seekToKill(nextKill + timeDiff + offset * 1000)" tertiary>
					Next kill
				</n-button>
				<n-button @click="genHighlight" tertiary v-if="selectedClips.length > 0">
					Create highlight
				</n-button>
			</n-flex>
			<n-checkbox-group v-model:value="selectedKills">
				<n-flex>
					<div
						v-for="kill in filterKills(currentMatch.kills)"
						:key="kill.time_in_match_in_ms"
						class="kill-button"
						:style="{
							border: 'solid 1px',
							borderRadius: '3px',
							borderColor:
								nextKillPreview === kill.time_in_match_in_ms
									? '#6d8cad'
									: 'rgba(255, 255, 255, 0.09)',
							transition: 'border-color 0.2s',
							padding: '5px 10px',
							display: 'flex',
							alignItems: 'center',
						}"
					>
						<n-checkbox
							:value="kill.time_in_match_in_ms + timeDiff + offset * 1000"
						></n-checkbox>
						<n-button
							@click="
								() =>
									seekToKill(kill.time_in_match_in_ms + timeDiff + offset * 1000)
							"
							text
							icon-placement="right"
							style="margin-left: 5px; margin-right: 5px"
						>
							Round {{ kill.round }} - {{ kill.weapon.name ?? "Knife" }}
							<template #icon>
								<n-icon size="16"><OpenOutline /></n-icon>
							</template>
						</n-button>
						<n-input-group
							v-if="
								selectedKills.includes(
									kill.time_in_match_in_ms + timeDiff + offset * 1000
								)
							"
						>
							<n-input-number
								style="max-width: 45px"
								placeholder=""
								:show-button="false"
								v-model:value="selectedOffsets[selectedKills.indexOf(kill.time_in_match_in_ms + timeDiff + offset * 1000)]![0]"
							></n-input-number>
							<n-input-group-label>-</n-input-group-label>
							<n-input-number
								:show-button="false"
								style="max-width: 45px"
								placeholder=""
								v-model:value="selectedOffsets[selectedKills.indexOf(kill.time_in_match_in_ms + timeDiff + offset * 1000)]![1]"
							></n-input-number>
						</n-input-group>
						<n-button
							style="margin-left: 5px"
							quaternary
							:style="{
								color:
									repeatClip !== null &&
									repeatClip ===
										selectedKills.indexOf(
											kill.time_in_match_in_ms + timeDiff + offset * 1000
										)
										? 'yellow'
										: 'white',
							}"
							round
							v-if="
								selectedKills.includes(
									kill.time_in_match_in_ms + timeDiff + offset * 1000
								)
							"
							@click="
								() =>
									setKillOnRepeat(
										selectedKills.indexOf(
											kill.time_in_match_in_ms + timeDiff + offset * 1000
										)
									)
							"
						>
							<template #icon>
								<n-icon size="16"><Reload /></n-icon>
							</template>
						</n-button>
					</div>
				</n-flex>
			</n-checkbox-group>
		</n-flex>
	</n-card>
</template>

<script setup lang="ts">
import {
	NCard,
	NFlex,
	NButton,
	NCheckbox,
	NIcon,
	NCheckboxGroup,
	NInputNumber,
	NInputGroup,
	NInputGroupLabel,
} from "naive-ui";
import { OpenOutline, Reload } from "@vicons/ionicons5";
import { useAccount, useSeekbar, usePlayer } from "~/store";

const accountStore = useAccount();
const seekbar = useSeekbar();
const player = usePlayer();

const currentMatch = ref();
const timeDiff = ref(0);
const selectedKills = ref<number[]>([]);
const selectedOffsets = ref<number[][]>([]);
const selectedClips = ref<number[][]>([]);
const repeatClip = ref<number | null>(null);

const progress = computed(() => seekbar.progress);
const streamStart = computed(() => accountStore.matchList.start);
const profile = computed(() => accountStore.profile);
const offset = computed(() => player.offset);

watch(
	() => selectedKills.value,
	(newSelectedKills) => {
		console.log("Selected kills updated:", newSelectedKills);
		selectedOffsets.value = newSelectedKills.map((kill, index) => {
			return selectedOffsets.value.length > index ? selectedOffsets.value[index]! : [-1, 2];
		});
		selectedClips.value = newSelectedKills.map((kill) => {
			return [Math.floor(kill / 1000) + -1, Math.floor(kill / 1000) + 2];
		});
	},
	{ deep: true }
);

watch(
	() => selectedOffsets.value,
	(newSelectedOffsets) => {
		console.log("Selected offsets updated:", newSelectedOffsets);
		selectedClips.value = newSelectedOffsets.map((offset, index) => {
			return [
				Math.floor(selectedKills.value[index]! / 1000) + offset[0]!,
				Math.floor(selectedKills.value[index]! / 1000) + offset[1]!,
			];
		});
	},
	{ deep: true }
);

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

const nextKillPreview = computed(() => {
	const kills = filterKills(currentMatch.value.kills);
	const ret = kills.filter((kill) => {
		return (
			kill.time_in_match_in_ms + timeDiff.value + offset.value * 1000 + 1000 >=
			progress.value * 1000
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
		// if last kill is less than 1 seconds before current time, return second last kill
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

const setKillOnRepeat = (index: number) => {
	if (repeatClip.value === index) {
		repeatClip.value = null;
	} else {
		repeatClip.value = index;
	}
};

const genHighlight = async () => {
	const data = await $fetch("/api/youtube/create-clip", {
		method: "POST",
		body: {
			kills: selectedClips.value,
			url: accountStore.matchList.url,
		},
	});

	console.log(data);
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

		if (repeatClip.value !== null) {
			const clip = selectedClips.value[repeatClip.value];
			if (clip && (newProgress >= clip[1]! || newProgress <= clip[0]!)) {
				player.YTplayer.seekTo(clip[0], true);
			}
		}
	},
	{ immediate: true }
);
</script>

<style scoped>
.kill-button .n-button {
	padding: 2px;
	height: auto;
}
</style>
