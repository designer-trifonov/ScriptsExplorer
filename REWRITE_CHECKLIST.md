# Чек-лист переписывания ScriptExplorer на Electron + vanilla JS/CSS

Правило: каждый файл ниже — это один существующий Python-скрипт (PySide6).
Когда его логика/визуал полностью перенесены в JS-эквивалент и проверены —
ставим `[x]`. Ничего не считается переписанным, пока не работает в Electron.

## 0. Точка входа и оркестрация
- [x] `main.py` → `main.js` (точка входа Electron, single-instance lock, создание окна)
- [x] `app_orchestrator.py` → `src/main/orchestrator.js` (жизненный цикл окна/трея/старт-кнопки)
- [x] `ui/main_window.py` → главное окно (Electron BrowserWindow + его события)
- [x] `ui/tray.py` → системный трей (Electron `Tray`)
- [x] `ui/start_button.py` → кнопка автозапуска/единственный процесс

## 1. Конфиг и тема
- [x] `data/config.py` → `src/shared/config.js` (settings.json + дефолты)
- [x] `ui/theme.py` → `src/renderer/theme.css` + `theme.js` (переменные цвета вместо QSS-шаблона)
- [x] `data/project_config.py` → `src/shared/projectConfig.js`

## 2. Данные о проекте (сканирование/анализ) — переносится как есть, логика не Qt-специфична
- [x] `data/models.py` → `src/shared/data/models.js` (ScriptInfo, MethodInfo + вычисляемые поля)
- [x] `data/lifecycle.py` → `src/shared/data/lifecycle.js`
- [x] `data/file_finder.py` → `src/shared/data/fileFinder.js`
- [x] `data/script_parser.py` → `src/shared/data/scriptParser.js`
- [x] `data/method_finder.py` → `src/shared/data/methodFinder.js`
- [x] `data/method_calls.py` → `src/shared/data/methodCalls.js`
- [x] `data/method_dependency_graph.py` → `src/shared/data/methodDependencyGraph.js`
- [x] `data/dependency_graph.py` → `src/shared/data/dependencyGraph.js`
- [x] `data/antipattern_checker.py` → `src/shared/data/antipatternChecker.js`
- [x] `data/dead_checker.py` → `src/shared/data/deadChecker.js`
- [x] `data/script_scanner.py` → `src/shared/data/scriptScanner.js`
- [x] `data/summary_builder.py` → `src/shared/data/summaryBuilder.js`
- [x] `data/project_store.py` → `src/shared/data/projectStore.js`

## 3. Хаб (список проектов)
- [x] `ui/hub.py` → `src/renderer/components/hub.js`

## 4. Экран проекта — верхний уровень
- [x] `ui/project_view.py` → `src/renderer/components/projectView.js`
- [x] `ui/project_toolbar.py` → `src/renderer/components/projectToolbar.js`
- [x] `ui/mode_toggle_button.py` → `src/renderer/components/modeToggleButton.js`
- [x] `ui/filter_bar.py` → `src/renderer/components/filterBar.js`
- [x] `ui/summary_dialog.py` → `src/renderer/components/summaryDialog.js`
- [x] `ui/script_detail.py` → `src/renderer/components/scriptDetail.js`
- [x] `ui/dependency_lane.py` → `src/renderer/components/dependencyLane.js`
- [x] `ui/connection_popup.py` → `src/renderer/components/connectionPopup.js`
- [x] `ui/base_dialog.py` → `src/renderer/components/baseDialog.js`

## 5. Карточки скриптов
- [x] `ui/cards/script_card.py` → `src/renderer/components/scriptCard.js`
- [x] `ui/cards/script_cell_view.py` → `src/renderer/components/scriptCellView.js`
- [x] `ui/cards/marquee_label.py` → `src/renderer/components/marqueeLabel.js`
- [x] `ui/cards/pill.py` → `src/renderer/components/pill.js`

## 6. Режим сетки
- [x] `ui/script_grid.py` → `src/renderer/components/scriptGrid.js`

## 7. Режим песочницы
- [x] `ui/sandbox_controller.py` → `src/renderer/components/sandboxController.js`
- [x] `ui/sandbox_canvas.py` → `src/renderer/components/sandboxCanvas.js`
- [x] `ui/sandbox_box_view.py` → `src/renderer/components/sandboxBoxView.js`
- [x] `data/sandbox_store.py` → `src/shared/data/sandboxStore.js`
- [x] `data/sandbox_new_position.py` → `src/shared/data/sandboxNewPosition.js`
- [x] `data/sandbox_grid_fill.py` → `src/shared/data/sandboxGridFill.js`
- [x] `data/sandbox_autosize.py` → `src/shared/data/sandboxAutosize.js`
- [x] `ui/sandbox_color_picker.py` → `src/renderer/components/sandboxColorPicker.js` (в оригинале нигде не вызывается — портировано как есть, неиспользуемая утилита)
- [x] `ui/sandbox_reflow_animation.py` → `src/renderer/components/sandboxReflowAnimation.js` (тоже нигде не вызывается в оригинале)
- [x] `ui/sandbox_drop_handler.py` → `src/renderer/components/sandboxDropHandler.js`
- [x] `ui/drop_target_finder.py` → `src/renderer/components/dropTargetFinder.js`
- [x] `ui/draggable_behavior.py` → `src/renderer/components/draggableBehavior.js`
- [x] `ui/draggable_script_card.py` → `src/renderer/components/draggableScriptCard.js`
- [x] `ui/bring_to_front.py` → `src/renderer/components/bringToFront.js`

## 8. Проверка после переноса (сквозные сценарии)
- [x] Открыть хаб → добавить/выбрать проект → сканирование запускается
- [x] Переключение фильтров меняет бейджи на карточках
- [x] Лента зависимостей открывается по клику на кнопку "Зависимости" (36 слотов на реальном проекте)
- [x] Диалог деталей скрипта открывается по клику на карточку
- [x] Переключение сетка ↔ песочница сохраняет положение скриптов
- [x] Drag карточки в песочнице, создание вложенной песочницы, drag песочницы в песочницу
- [x] Сессия песочницы переживает перезапуск приложения (загружена реальная сессия пользователя, созданная ещё в Python-версии)
- [x] Трей + кнопка автозапуска + единственный экземпляр процесса работают

---
**Прогресс:** 51 / 51 файлов — переписывание завершено.
