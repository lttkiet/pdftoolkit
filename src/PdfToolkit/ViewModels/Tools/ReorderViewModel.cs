using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PdfSharp.Pdf;
using PdfSharp.Pdf.IO;

namespace PdfToolkit.ViewModels.Tools;

public partial class ReorderViewModel : ViewModelBase
{
    private readonly MainWindowViewModel _mainVm;
    private readonly List<int> _pageOrder = new();
    private PdfDocument? _sourceDoc;

    public ObservableCollection<string> PageList { get; } = new();

    [ObservableProperty]
    private int _selectedIndex = -1;

    public ReorderViewModel(MainWindowViewModel mainVm)
    {
        _mainVm = mainVm;
    }

    [RelayCommand]
    private async Task LoadAsync()
    {
        var path = await _mainVm.FileDialogService.OpenPdfAsync(GetWindow());
        if (path == null) return;

        try
        {
            _sourceDoc?.Dispose();
            _sourceDoc = PdfReader.Open(path, PdfDocumentOpenMode.Import);

            _pageOrder.Clear();
            PageList.Clear();

            for (var i = 0; i < _sourceDoc.PageCount; i++)
            {
                _pageOrder.Add(i);
                PageList.Add($"Page {i + 1}");
            }

            SelectedIndex = 0;
            _mainVm.StatusText = $"Loaded: {Path.GetFileName(path)} ({_sourceDoc.PageCount} pages)";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Load failed: {ex.Message}";
        }
    }

    [RelayCommand]
    private void MoveUp()
    {
        if (SelectedIndex <= 0) return;

        var pageIdx = _pageOrder[SelectedIndex];
        _pageOrder.RemoveAt(SelectedIndex);
        _pageOrder.Insert(SelectedIndex - 1, pageIdx);

        var item = PageList[SelectedIndex];
        PageList.RemoveAt(SelectedIndex);
        PageList.Insert(SelectedIndex - 1, item);

        SelectedIndex--;
    }

    [RelayCommand]
    private void MoveDown()
    {
        if (SelectedIndex < 0 || SelectedIndex >= PageList.Count - 1) return;

        var pageIdx = _pageOrder[SelectedIndex];
        _pageOrder.RemoveAt(SelectedIndex);
        _pageOrder.Insert(SelectedIndex + 1, pageIdx);

        var item = PageList[SelectedIndex];
        PageList.RemoveAt(SelectedIndex);
        PageList.Insert(SelectedIndex + 1, item);

        SelectedIndex++;
    }

    [RelayCommand]
    private async Task SaveAsync()
    {
        if (_sourceDoc == null || PageList.Count == 0)
        {
            _mainVm.StatusText = "No document loaded";
            return;
        }

        var savePath = await _mainVm.FileDialogService.SavePdfAsync(GetWindow(), "reordered.pdf");
        if (savePath == null) return;

        try
        {
            using var result = new PdfDocument();

            foreach (var origIndex in _pageOrder)
                result.AddPage(_sourceDoc.Pages[origIndex]);

            result.Save(savePath);
            _mainVm.StatusText = $"Saved reordered PDF ({result.PageCount} pages)";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Save failed: {ex.Message}";
        }
    }
}
