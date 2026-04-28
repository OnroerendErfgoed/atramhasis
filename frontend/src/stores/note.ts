import type { Note } from '@models/util';
import { useAdminUiStore } from '@stores/admin-ui';
import { defineStore, storeToRefs } from 'pinia';
import { ref, watch } from 'vue';

export const useNoteStore = defineStore('note', () => {
  const adminUiStore = useAdminUiStore();
  const { noteModalIsOpen } = storeToRefs(adminUiStore);

  const selectedNote = ref<Note>();

  const setSelectedNote = (note: Note) => {
    selectedNote.value = note;
  };

  const resetSelectedNote = () => {
    selectedNote.value = undefined;
  };

  watch(noteModalIsOpen, (open) => {
    if (!open && selectedNote.value) {
      resetSelectedNote();
    }
  });

  return { selectedNote, setSelectedNote, resetSelectedNote };
});
