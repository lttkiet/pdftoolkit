using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using CommunityToolkit.Mvvm.ComponentModel;

namespace PdfToolkit.ViewModels;

public abstract class ViewModelBase : ObservableObject
{
    protected static Window GetWindow()
    {
        var desktop = (IClassicDesktopStyleApplicationLifetime)Application.Current!.ApplicationLifetime!;
        return desktop.MainWindow!;
    }
}
