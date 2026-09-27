<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
const trips = ref<any[]>([])
const events = ref<any[]>([])
const savedTip = ref('')
async function loadEvents() {
  try {
    events.value = (await api('/reports/run?line_id=1', { method: 'POST' })).events || []
  } catch { events.value = [] }
}
onMounted(async () => {
  trips.value = await api('/trips')
  await loadEvents()
})
async function saveVehicle(r: any, ev: Event) {
  const v = ((ev.target as HTMLInputElement).value || '').trim()
  if (v === r.vehicle_no) return
  const updated = await api(`/trips/${r.id}`, { method: 'PATCH', body: JSON.stringify({ vehicle_no: v }) })
  r.vehicle_no = updated.vehicle_no
  savedTip.value = `${r.trip_no} 车号已保存`
  setTimeout(() => { savedTip.value = '' }, 1500)
  await loadEvents() // 车号变化影响同车接续判定，刷新条带
}
function stripClass(s: string) {
  return s === 'bunching' ? 'bg-bunch' : s === 'large_gap' ? 'bg-large' : s === 'same_vehicle' ? 'bg-same' : ''
}
function badgeClass(s: string) {
  return s === 'bunching' ? 'badge-bad' : s === 'large_gap' ? 'badge-warn' : s === 'same_vehicle' ? 'badge-dim' : 'badge-ok'
}
function label(s: string) {
  return s === 'bunching' ? '串车' : s === 'large_gap' ? '大间隔' : s === 'same_vehicle' ? '同车接续' : '正常'
}
</script>
<template>
  <h1>班次 · 间隔条带</h1>
  <p class="sub">左侧班次清单（车号可改，失焦保存），右侧串车/间隔竖直条带</p>
  <p v-if="savedTip" class="muted">{{ savedTip }}</p>
  <div class="bg-split">
    <aside class="bg-trip-col">
      <h2>班次列表</h2>
      <div v-for="r in trips" :key="r.id ?? r.trip_no" class="bg-trip-row">
        <div>
          <div>{{ r.trip_no }}</div>
          <div class="bg-trip-meta">
            线路 {{ r.line_id }} · 车
            <input
              class="bg-veh-input"
              :value="r.vehicle_no"
              placeholder="未填车号"
              @change="saveVehicle(r, $event)"
            />
          </div>
        </div>
        <div class="bg-trip-meta">{{ r.planned_depart }}</div>
      </div>
    </aside>
    <div class="bg-strip-col">
      <article
        v-for="(e, i) in events"
        :key="i"
        class="bg-gap-strip"
        :class="stripClass(e.status)"
      >
        <header>{{ e.stop_name }}</header>
        <div class="bg-gap-body">
          <div class="bg-gap-val">{{ e.gap_min }}′</div>
          <div>计划 {{ e.planned_headway_min }}′</div>
          <div>{{ e.earlier_trip }} → {{ e.later_trip }}</div>
          <span class="badge" :class="badgeClass(e.status)">
            {{ label(e.status) }}
          </span>
        </div>
      </article>
      <p v-if="!events.length" class="muted">暂无间隔事件</p>
    </div>
  </div>
</template>
