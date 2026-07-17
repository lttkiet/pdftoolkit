using Avalonia.Controls;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PdfToolkit.Models;
using PdfToolkit.Services;

namespace PdfToolkit.ViewModels;

public partial class MainWindowViewModel : ViewModelBase
{
    private readonly DocumentModel _documentModel = new();
    private readonly IFileDialogService _fileDialogService = new FileDialogService();
    private Window? _window;

    public DocumentModel DocumentModel => _documentModel;
    public IFileDialogService FileDialogService => _fileDialogService;

    [ObservableProperty]
    private string _statusText = "Ready";

    [ObservableProperty]
    private int _selectedToolIndex;

    [ObservableProperty]
    private UserControl? _currentToolView;

    private readonly Dictionary<int, UserControl> _toolViews = new();

    public List<ToolItem> Tools { get; } =
    [
        new() { Name = "Viewer", Tooltip = "Open and view PDF files", Icon = "📖" },
        new() { Name = "Merge", Tooltip = "Combine multiple PDFs into one", Icon = "🔗" },
        new() { Name = "Split", Tooltip = "Split PDF into separate files", Icon = "✂" },
        new() { Name = "Rotate", Tooltip = "Rotate pages by 90/180/270 degrees", Icon = "🔄" },
        new() { Name = "Reorder", Tooltip = "Drag to reorder pages", Icon = "📋" },
        new() { Name = "Add Content", Tooltip = "Add text or image overlays", Icon = "📝" },
        new() { Name = "Extract Text", Tooltip = "Extract text from pages", Icon = "📄" },
        new() { Name = "Compress", Tooltip = "Reduce PDF file size", Icon = "📦" },
        new() { Name = "Watermark", Tooltip = "Add watermark to pages", Icon = "💧" },
        new() { Name = "Encrypt", Tooltip = "Password protect or decrypt PDFs", Icon = "🔒" },
        new() { Name = "Convert", Tooltip = "Convert between PDF and images", Icon = "🔄" },
        new() { Name = "Metadata", Tooltip = "View and edit PDF metadata", Icon = "ℹ" },
    ];

    public void SetWindow(Window window)
    {
        _window = window;
    }

    partial void OnSelectedToolIndexChanged(int value)
    {
        LoadToolView(value);
    }

    private void LoadToolView(int index)
    {
        if (_window == null) return;

        if (_toolViews.TryGetValue(index, out var existing))
        {
            CurrentToolView = existing;
            return;
        }

        UserControl view = index switch
        {
            0 => new Views.ViewerView { DataContext = new ViewerViewModel(this) },
            1 => new Views.Tools.MergeView { DataContext = new Tools.MergeViewModel(this) },
            2 => new Views.Tools.SplitView { DataContext = new Tools.SplitViewModel(this) },
            3 => new Views.Tools.RotateView { DataContext = new Tools.RotateViewModel(this) },
            4 => new Views.Tools.ReorderView { DataContext = new Tools.ReorderViewModel(this) },
            5 => new Views.Tools.AddContentView { DataContext = new Tools.AddContentViewModel(this) },
            6 => new Views.Tools.ExtractTextView { DataContext = new Tools.ExtractTextViewModel(this) },
            7 => new Views.Tools.CompressView { DataContext = new Tools.CompressViewModel(this) },
            8 => new Views.Tools.WatermarkView { DataContext = new Tools.WatermarkViewModel(this) },
            9 => new Views.Tools.EncryptView { DataContext = new Tools.EncryptViewModel(this) },
            10 => new Views.Tools.ConvertView { DataContext = new Tools.ConvertViewModel(this) },
            11 => new Views.Tools.MetadataView { DataContext = new Tools.MetadataViewModel(this) },
            _ => new Views.ViewerView { DataContext = new ViewerViewModel(this) },
        };

        _toolViews[index] = view;
        CurrentToolView = view;
    }

    [RelayCommand]
    private async Task OpenPdfAsync()
    {
        if (_window == null) return;
        var path = await _fileDialogService.OpenPdfAsync(_window);
        if (path == null) return;

        try
        {
            _documentModel.Open(path);
            StatusText = $"Opened: {System.IO.Path.GetFileName(path)} ({_documentModel.PageCount} pages)";

            SelectedToolIndex = 0;
            if (_toolViews.TryGetValue(0, out var viewer) && viewer.DataContext is ViewerViewModel vm)
            {
                vm.LoadDocument();
            }
        }
        catch (Exception ex)
        {
            StatusText = $"Error: {ex.Message}";
        }
    }
}
