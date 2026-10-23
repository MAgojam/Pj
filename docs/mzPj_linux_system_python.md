# System Python from jamovi on Linux Flatpak

When System Python is selected, Pj/Pjp use `flatpak-spawn --host` to start
`/usr/bin/python3` on the host computer. This requires access to the
`org.freedesktop.Flatpak` session-bus service. The embedded jamovi Python runs
inside the application and does not use this host-execution permission.

If Flatpak reports `ServiceUnknown`, `AccessDenied` or its explicit host-access
hint before Python starts, Pj/Pjp display **System Python setup** with these
instructions. A selected interpreter is executed through the normal backend
lifecycle; Pj does not grant permissions or run setup commands automatically.

Close all jamovi windows before changing how it starts. In a Linux terminal,
choose one of the following approaches.

## Temporary access for one launch

```bash
flatpak run --talk-name=org.freedesktop.Flatpak org.jamovi.jamovi
```

This applies only to that launch. Select System Python and run the script again.

## Persistent setting for the current user

```bash
flatpak override --user --talk-name=org.freedesktop.Flatpak org.jamovi.jamovi
```

Then reopen jamovi normally, including from its desktop icon. The permission
allows jamovi to start processes outside its Flatpak container, on the host.
Pj does not apply this setting itself.

If the same error remains, check that the Flatpak host service is available in
the Linux session. The original diagnostic is available in a collapsed section
of the result. Other Python launch failures and script/import errors retain
their own diagnostics rather than being mislabeled as a Flatpak permission issue.

This setup help is specific to **Linux Flatpak + System Python**. Windows,
macOS, non-Flatpak Linux and embedded Python do not display this message.

Reference: [Flatpak command documentation](https://docs.flatpak.org/en/latest/flatpak-command-reference.html#flatpak-spawn).
