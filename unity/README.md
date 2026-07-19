# Unity mobile client — Modo B (Arena Live 3D)

Cliente do **Modo B — Arena Live 3D** (**iOS / Android**). Scaffold UNI-01: empty scene, sem gameplay.

O **Modo A — Arena Quests** (Angular, camadas, personalidade, judge) vive em `frontend/` + `quests/` e permanece ativo em paralelo — esta pasta não o substitui.

## Editor (versão travada)

| Campo | Valor |
|-------|-------|
| Unity | **6.3 LTS** |
| Build | `6000.3.20f1` |
| Revision | `c9ba695d4f07` |
| Hub | `unityhub://6000.3.20f1/c9ba695d4f07` |

Instale exatamente esta build via [Unity Hub](https://unity.com/download) (Installs → Install Editor → Archive se necessário). Não abra com major diferente sem bump de spec.

### Módulos obrigatórios no Editor

- **Android Build Support** (SDK + NDK + OpenJDK)
- **iOS Build Support** (build de Xcode exige macOS)

Pacotes UPM já no `Packages/manifest.json`: Input System, uGUI + módulos builtin usados pelo scaffold.

## Abrir o projeto

1. Clone o monorepo.
2. Unity Hub → **Open** → selecione a pasta `unity/` (não a raiz do repo).
3. Aguarde o primeiro import (`Library/` é gerada localmente e está no `.gitignore`).
4. Abra a cena `Assets/Scenes/Boot.unity` (já está em **Build Profiles / Build Settings** como cena 0).

Se o Hub pedir upgrade de versão, **cancele** e instale `6000.3.20f1`.

## Estrutura

```text
unity/
├── Assets/
│   ├── Scenes/Boot.unity   # bootstrap (empty scene)
│   ├── Scripts/            # placeholder até UNI-08+
│   └── Settings/           # reservado para assets de projeto
├── Packages/               # manifest + lock
├── ProjectSettings/        # Player Android/iOS, Build Settings
├── .gitignore
└── README.md
```

## Build empty scene (Android)

Pré-requisitos: módulo Android instalado; device/emulator com USB debugging ou gerar APK/AAB.

1. File → **Build Profiles** (ou Build Settings) → plataforma **Android**.
2. Confirme `Assets/Scenes/Boot` na Scene List (enabled).
3. Player Settings já definem:
   - Package Name: `com.agentbattlearena.mobile`
   - Min API: 24
   - Scripting Backend: IL2CPP
   - Target Architectures: ARM64
4. **Build** (ou Build And Run) → escolha pasta local (ex.: `unity/Builds/Android/`; ignorada pelo git).

## Build empty scene (iOS)

Pré-requisitos: macOS + Xcode; módulo iOS no Editor.

1. File → **Build Profiles** → plataforma **iOS**.
2. Confirme cena `Boot` na Scene List.
3. Player Settings: Bundle ID `com.agentbattlearena.mobile`, Target minimum iOS 15.0, IL2CPP.
4. **Build** → pasta local (ex.: `unity/Builds/iOS/`).
5. Abra o `.xcodeproj` / workspace gerado no Xcode → selecione team de signing → Run no device/simulador.

## Git

Não commitar `Library/`, `Temp/`, `Obj/`, `Logs/`, `UserSettings/`, nem builds locais — cobertos por `unity/.gitignore`.

Commitar: `Assets/`, `Packages/`, `ProjectSettings/`, este README.

## Fora deste scaffold

Gameplay, NavMesh, sync com backend, auth e CI de build Unity ficam nas specs UNI-02+ (só Modo B).
