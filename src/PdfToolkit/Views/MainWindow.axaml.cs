using Avalonia.Controls;
using Avalonia.Input;
using PdfToolkit.ViewModels;

namespace PdfToolkit.Views;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();

        if (DataContext is MainWindowViewModel vm)
            vm.SetWindow(this);

        KeyDown += OnKeyDown;
    }

    protected override void OnResized(WindowResizedEventArgs e)
    {
        base.OnResized(e);
        if (DataContext is MainWindowViewModel vm)
            vm.UpdateLayoutForWidth(ClientSize.Width);
    }

    private void OnKeyDown(object? sender, KeyEventArgs e)
    {
        if (DataContext is not MainWindowViewModel vm) return;

        if (e.KeyModifiers == KeyModifiers.Control && e.Key == Key.O)
        {
            vm.OpenPdfCommand.Execute(null);
            e.Handled = true;
        }
    }
}
