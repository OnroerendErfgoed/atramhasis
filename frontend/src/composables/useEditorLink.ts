import { ref } from 'vue';
import type { EditorCustomHandlers } from '@nuxt/ui';

type TiptapEditor = Parameters<EditorCustomHandlers[string]['execute']>[0];

export interface HoveredLink {
  href: string;
  top: number;
  left: number;
}

export function useEditorLink() {
  const linkModalOpen = ref(false);
  const linkUrl = ref('');
  const isLinkActive = ref(false);
  let currentEditor: TiptapEditor | null = null;
  let savedSelection: { from: number; to: number } | null = null;

  const hoveredLink = ref<HoveredLink | null>(null);

  function onEditorMouseover(event: MouseEvent) {
    const anchor = (event.target as HTMLElement).closest('a[href]') as HTMLAnchorElement | null;
    if (anchor) {
      const rect = anchor.getBoundingClientRect();
      hoveredLink.value = {
        href: anchor.getAttribute('href') ?? '',
        top: rect.bottom + 4,
        left: rect.left,
      };
    } else {
      hoveredLink.value = null;
    }
  }

  function onEditorMouseleave() {
    hoveredLink.value = null;
  }

  const customHandlers = {
    customLink: {
      canExecute: () => true,
      execute: (editor) => {
        currentEditor = editor;
        isLinkActive.value = editor.isActive('link');
        linkUrl.value = editor.getAttributes('link').href ?? '';
        const { from, to } = editor.state.selection;
        savedSelection = { from, to };
        linkModalOpen.value = true;
        return editor.chain();
      },
      isActive: (editor) => editor.isActive('link'),
      isDisabled: (editor) => editor.state.selection.empty && !editor.isActive('link'),
    },
  } satisfies EditorCustomHandlers;

  function saveLink() {
    if (!currentEditor || !linkUrl.value.trim()) return;
    const chain = currentEditor.chain().focus();
    if (savedSelection) chain.setTextSelection(savedSelection);
    chain.extendMarkRange('link').setLink({ href: linkUrl.value.trim() }).run();
    linkUrl.value = '';
    savedSelection = null;
    linkModalOpen.value = false;
  }

  function removeLink() {
    if (!currentEditor) return;
    const chain = currentEditor.chain().focus();
    if (savedSelection) chain.setTextSelection(savedSelection);
    chain.extendMarkRange('link').unsetLink().run();
    linkUrl.value = '';
    savedSelection = null;
    linkModalOpen.value = false;
  }

  return {
    customHandlers,
    linkModalOpen,
    linkUrl,
    isLinkActive,
    saveLink,
    removeLink,
    hoveredLink,
    onEditorMouseover,
    onEditorMouseleave,
  };
}
